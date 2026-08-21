# WALL ART — Production MVP Build Prompt (Multi-Agent Orchestration)

## 0. How to use this document

This is a master orchestration prompt for building the "Wall Art" personalised photo-to-vinyl-graphic ecommerce platform as a **real, deployable production system** — not a sandbox, not a proof-of-concept demo repo. Feed the "Orchestrator" section to your lead agent (e.g. Claude Code running as coordinator), and spin up the sub-agents below as it works through each milestone. Each sub-agent section is self-contained enough to hand to a separate agent/session with only its own scope in context, plus the shared contracts in Section 2.

Do not stub, mock, or fake any requirement. Every checkbox in Section 7 must correspond to working code, a real integration, or a documented manual process — not a placeholder.

---

## 1. Orchestrator Agent — system prompt

```
You are the Lead Architect and Orchestrator for "Wall Art," a production ecommerce
platform that turns a customer's uploaded photo into an original AI-generated
character artwork, printed and sold as a physical vinyl wall graphic.

Your job is not to write every line of code yourself. Your job is to:
1. Own the architecture decision (Section 3) and never let a sub-agent silently
   deviate from it.
2. Decompose work into the 8 sub-agents defined in Section 4, hand each one its
   scoped brief plus the shared contracts (Section 2), and sequence them per the
   dependency graph (Section 5).
3. After each sub-agent reports work done, verify it against the Definition of
   Done in Section 7 for that milestone BEFORE marking it complete. Re-open work
   that doesn't meet it — do not accept "mostly working" or "works in my test."
4. Maintain a single source of truth: /docs/architecture.md, /docs/api-contract.md,
   /docs/decisions.md (ADR log). Every sub-agent must read these before writing
   code and update them when they change something structural.
5. Treat this as a real product with real money, real customer photos (some of
   children), and real legal exposure (UK GDPR, IP infringement, PCI scope via
   Stripe). Refuse to let any agent take a shortcut that would create a genuine
   compliance or safety gap — flag it to the human operator instead of quietly
   working around it.
6. Nothing ships to production behind a payment or upload wall without: HTTPS
   everywhere, signed URLs for private image storage, webhook signature
   verification, and passing the security checklist in Section 7.5.

Do not proceed to Milestone 2 until Milestone 1's proof-of-concept generation
pipeline has been run end-to-end on at least 5 real sample photos with acceptable
likeness, and cost-per-generation has been measured and logged in /docs/decisions.md.
```

---

## 2. Shared contracts (every agent reads this first)

### 2.1 Chosen architecture (do not relitigate without an ADR)

- **Not Base44.** Rebuild on a conventional stack for ownership, security control over private/child photos, and long-term maintainability. Base44 is a no-code platform; this product has custom async AI pipelines, signed-URL private storage, and PCI-adjacent payment flows that need full backend control the client will own outright.
- **Frontend:** React + TypeScript (Vite), Tailwind, deployed as a static SPA (or Next.js if SEO on marketing/theme pages matters — Orchestrator decides and logs an ADR).
- **Backend:** FastAPI (Python 3.12), async, deployed as containerized service on AWS ECS Fargate (or Lambda for the API layer if traffic is low and cold-start is acceptable — log the decision).
- **Database:** PostgreSQL (RDS), with a job/queue table for generation status.
- **Async job processing:** Redis + RQ or Celery, or AWS SQS + Lambda worker, for image-generation jobs (must not block the request/response cycle — generation takes 10–60s+).
- **Object storage:** S3, private buckets, signed URLs with short expiry for both customer previews and admin production-file downloads.
- **Payments:** Stripe Checkout + webhooks (webhook signature verification mandatory).
- **Email:** SES or Postmark/Resend for transactional confirmation emails.
- **Hosting/infra:** AWS (matches existing production stack: ECS/Lambda, RDS, S3, CloudFront for the SPA, Route 53 for the client's domain).
- **Monitoring:** CloudWatch + a lightweight error tracker (Sentry) from day one — not added later.
- **All third-party accounts (Stripe, AWS, AI provider, email) created under the client's own billing/ownership, per the brief's IP/ownership requirement.**

### 2.2 AI image pipeline decision

- **Primary model:** an image-to-image identity-preserving pipeline, not vanilla text-to-image. Recommend evaluating, in Milestone 1, against real sample photos:
  - **InstantID** or **PhotoMaker** (face-ID conditioning on top of a diffusion base) — good likeness retention, open weights, can self-host on GPU (Replicate/Modal/RunPod) or call via a hosted API.
  - **Flux.1 [dev/pro] with IP-Adapter FaceID / ControlNet**, hosted via **Replicate** or **fal.ai** — currently strong likeness + style transformation quality, pay-per-generation, no infra to manage.
  - Fallback/comparison: **Google Gemini image editing** or **OpenAI's image API** for a fully managed alternative if self-hosted/Replicate quality or reliability is insufficient — check their commercial-use and processing terms for the "no training on customer images" requirement before committing.
- **Decision criteria to lock in during Milestone 1 POC:** likeness score (manual review against a rubric), consistency across 5+ diverse test photos, generation latency, cost per image, commercial usage rights, and whether the provider contractually excludes customer images from training data.
- **Background removal / subject isolation:** dedicated model (e.g. **rembg**/**BiRefNet** self-hosted, or a hosted API like **remove.bg**/**Clipdrop**) run as a separate pipeline stage after generation — do not rely on the generation model to produce a clean alpha channel.
- **Upscaling:** a dedicated upscaler (e.g. **Real-ESRGAN**, or Replicate/Clipdrop upscale endpoints) to take the generation output up to print resolution — see Section 4.3 for target DPI.
- **Two distinct output artifacts per approved order:** (1) watermarked, lower-res, sRGB preview shown to the customer pre-payment; (2) full-res, upscaled, background-processed production file, generated/finalized only after payment and never exposed to the customer directly.

### 2.3 Data model (minimum viable schema — agents extend, don't shrink)

```
users            (customers — email, optional account, created_at)
orders           (id, user_id, status, theme_id, product_size, price, stripe_payment_id,
                  shipping_address, created_at, updated_at)
order_statuses   (New, Awaiting Approval, Paid, In Production, Dispatched, Cancelled, Refunded)
uploads          (id, order_id, s3_key_original, consent_confirmed_at, quality_check_result)
generations      (id, order_id, upload_id, theme_id, instructions_text, status,
                  provider, model_version, s3_key_preview, s3_key_production,
                  cost_usd, generation_time_ms, attempt_number, failure_reason)
themes           (id, name, prompt_template, active, sort_order)
regeneration_log (id, order_id, generation_id, requested_at, reason)
audit_log        (id, actor_type[customer/admin/system], action, order_id, created_at)
retention_policy (applies at the account/global level — deletion job runs against uploads/generations by age)
```

### 2.4 API contract skeleton (backend agent finalizes in `/docs/api-contract.md`)

```
POST   /api/themes                          -> list active themes
POST   /api/uploads                          -> presigned S3 upload URL + consent flag
POST   /api/orders                           -> create draft order (theme, upload_id, instructions)
POST   /api/orders/{id}/generate             -> enqueue generation job
GET    /api/orders/{id}/generation-status    -> poll or SSE/websocket for progress
POST   /api/orders/{id}/regenerate           -> limited regeneration (enforce per-order cap)
POST   /api/orders/{id}/approve              -> customer approves preview
POST   /api/orders/{id}/checkout-session     -> create Stripe Checkout session
POST   /api/webhooks/stripe                  -> payment confirmation (signature-verified)
GET    /api/orders/{id}/confirmation         -> order confirmation page data

-- Admin (authenticated, role-gated) --
GET    /api/admin/orders                     -> list/search/filter
GET    /api/admin/orders/{id}                -> full detail incl. original photo, all generations
POST   /api/admin/orders/{id}/regenerate      -> authorized manual regen
POST   /api/admin/orders/{id}/status          -> update production status
GET    /api/admin/orders/{id}/production-file -> signed download URL, logged in audit_log
DELETE /api/admin/orders/{id}/photos          -> manual deletion tool
GET    /api/admin/costs                       -> AI generation cost dashboard
GET    /api/admin/themes / POST / PATCH       -> theme management
```

---

## 3. Non-negotiable product requirements (traceable to the brief — do not drop any of these)

- Image-to-image only; never fall back to text-to-image-from-scratch.
- Strong, recognisable facial likeness preserved in every output.
- Fully original character designs — **no named superheroes, no football club badges/kits, no film/TV characters, no third-party logos.** Theme prompt templates must be reviewed against this before going live, and free-text customer instructions must be filtered/moderated against it.
- Two-tier output: watermarked low-res preview pre-payment, high-res production file gated behind payment confirmation.
- Consent capture ("I own this photo or have permission to use it") stored against the upload, not just shown and discarded.
- Private, signed-URL-only image storage. No public S3 buckets. No API keys in frontend code.
- Configurable retention period with an automated deletion job, plus a manual admin deletion tool and a documented per-customer deletion process (UK GDPR right to erasure).
- No use of customer photos for AI model training, and no reuse in portfolios/marketing without separate written permission — this must be contractually true of whichever AI provider is chosen, not just a policy statement.
- Rate limiting and abuse protection on upload/generation endpoints; a policy decision (Section 4.4) on what gates generation (payment vs. deposit vs. email verification) to control AI spend.
- All third-party accounts (Stripe, AWS, AI provider) provisioned under the client's own ownership.

---

## 4. Sub-agents

### 4.1 Frontend Agent (Customer Journey)

**Scope:** React + TypeScript SPA covering the full customer journey end to end.

**Deliverables:**
- Theme gallery (pulls from `/api/themes`, admin-manageable).
- Upload flow: drag/drop + mobile camera capture, client-side file-type/size validation, then presigned-URL upload directly to S3 (never proxy large files through the API server).
- Consent checkbox gating upload submission, stored via the API, not just a client-side flag.
- Optional instructions field with a visible character limit and a client-side hint about disallowed content (branded characters, real people other than the uploaded subject, etc.) — actual enforcement is server-side (Section 4.4).
- Generation progress screen: poll `/generation-status` or subscribe via SSE/websocket; handle timeout, retry, and failure states with clear customer-facing messaging (never a raw stack trace).
- Watermarked preview screen with Approve / Regenerate (enforce visible remaining-regeneration count from the API).
- Product size/options selector with live price calculation.
- Checkout: delivery details form (UK address validation), Stripe Checkout redirect or embedded Elements.
- Order confirmation page + expectation-setting copy ("You'll receive a confirmation email; production begins after...").
- Responsive (mobile/tablet/desktop), basic accessibility (labelled form fields, keyboard navigation, sufficient contrast), basic SEO (meta tags, semantic headings) on marketing/theme pages.
- Privacy/terms/consent content pages, linked from the upload step, not just the footer.

**Must not:** embed any API secret or AI provider key; call the AI provider directly from the browser; store the original high-res photo or production file client-side beyond what's needed to display it.

### 4.2 Backend / Orders API Agent

**Scope:** FastAPI service owning orders, uploads metadata, themes, auth for the admin side, and orchestration of the async generation job (calls into the AI Pipeline Agent's worker, doesn't reimplement it).

**Deliverables:**
- All customer-facing endpoints in Section 2.4.
- Presigned S3 upload URL issuance with strict content-type/size limits enforced server-side (never trust the client).
- Basic image-quality validation (resolution floor, blur/face-detection sanity check — a lightweight check, e.g. using a face-detection library, before accepting the upload as generation-ready) — reject with a clear reason if it fails.
- Order/generation state machine matching the statuses in Section 2.3, with valid-transition enforcement (e.g. can't mark "Dispatched" before "Paid").
- Enqueue generation jobs onto the async queue; never run generation synchronously in the request handler.
- Duplicate-order prevention (idempotency keys on order/checkout creation).
- Structured logging that **excludes** raw image bytes/base64 from logs; log metadata (order id, status, timing, cost) only.
- Auth: admin login (email/password or SSO — Orchestrator decides and logs ADR) with role-based access; customer side can be guest-checkout (email-only) for MVP per the brief's "advanced accounts not required" scope note.

### 4.3 AI Image Pipeline Agent

**Scope:** the async worker(s) that take an uploaded photo + theme + instructions and produce the two output artifacts.

**Deliverables:**
- Pipeline stages, each independently retryable and logged: (1) input validation/face detection, (2) identity-preserving image-to-image generation against the chosen model (Section 2.2), (3) background removal/subject isolation, (4) upscale to production resolution, (5) watermark the preview copy, (6) write both artifacts to S3 under signed, order-scoped keys, (7) update generation status + cost + timing on the order record.
- **Production resolution target:** derive from the largest advertised wall-graphic size at print-quality DPI (typically 150–300 DPI for large-format vinyl viewed at distance — confirm with the client's print vendor, document the chosen DPI and max practical printed dimensions in `/docs/architecture.md`, and size the upscaler's target accordingly).
- **File format:** transparent PNG (or TIFF if the print vendor requires it) for the production file; sRGB preview; document any colour-profile conversion needed for the vendor's press (many large-format printers want CMYK-converted or a specific ICC profile — flag this as a print-vendor coordination item rather than guessing).
- Defect detection: automated sanity checks (e.g. face-detection confidence on the *output*, not just input, to catch generations where the face was lost/distorted) plus the manual admin approve/reject step as the real backstop for MVP.
- Regeneration allowance enforcement (reads limit from theme/global config, not hardcoded).
- Content/prompt moderation layer: theme prompt templates hard-coded to avoid protected IP; free-text customer instructions passed through a moderation check (a simple keyword/entity blocklist plus, ideally, a moderation API call) before being merged into the generation prompt — reject or strip disallowed content server-side, don't rely on the frontend hint alone.
- Cost logging per generation (provider's actual billed cost or a documented estimate), surfaced to the admin cost dashboard.
- Timeout + retry policy (e.g. 2 retries with backoff, then mark failed and surface a clear customer message + admin alert).

**Report back to Orchestrator after Milestone 1:** measured likeness quality (qualitative, on ≥5 real test photos), average generation time, actual cost per successful image, and the AI provider's contractual position on training-data use and commercial rights — this gates Milestone 2.

### 4.4 Payments & Abuse-Control Agent

**Scope:** Stripe integration and the anti-abuse/cost-control policy layer.

**Deliverables:**
- Stripe Checkout session creation, webhook endpoint with signature verification, idempotent webhook handling (Stripe can retry/duplicate delivery).
- Payment states mapped onto order status; refund/cancellation support (admin-triggered, calling Stripe's refund API and updating order status + a production note).
- **Explicit recommendation to the Orchestrator, logged as an ADR, on what gates generation:** given the brief's own openness on this, default recommendation is: free preview generation gated by **email verification + rate limiting per email/IP + a hard cap on free generations per session** (not a paid deposit, to preserve the low-friction "preview before you buy" journey the brief prefers), with the **high-resolution production file always gated behind confirmed payment** regardless. Document the actual chosen approach and its reasoning in `/docs/decisions.md`.
- Rate limiting on `/uploads`, `/generate`, and `/regenerate` (per-IP and per-email), returning clear 429s the frontend can display.
- Generation-cost circuit breaker: a configurable daily/monthly AI-spend cap that pauses new free generations (not paid ones) and alerts the admin if exceeded.

### 4.5 Admin Dashboard Agent

**Scope:** the internal-facing app (can be a protected route within the same React app or a separate admin SPA — Orchestrator decides).

**Deliverables — full checklist from the brief, all required:**
- Orders list with search/filter (by status, date, theme, customer email).
- Order detail: customer contact + delivery info, original photo, all generation attempts (preview + production), selected theme + instructions, selected size/options, generation status, payment status.
- Signed-URL download of the high-resolution production file (logged in `audit_log`).
- Manual "regenerate" action (authorized/logged), approve/reject artwork action.
- Status update control across the full status set (Section 2.3), with production notes field.
- AI cost visibility (per-order and aggregate, from `/api/admin/costs`).
- Theme management (add/edit/deactivate themes, prompt templates, prices, regeneration allowance) — practical MVP-level CRUD, not necessarily a rich CMS.
- Manual photo/generation deletion tool wired to actually delete the S3 objects, not just hide the DB row.

### 4.6 Privacy, Security & Compliance Agent

**Scope:** cross-cutting — reviews and hardens every other agent's output rather than owning a single feature slice. Runs in parallel from Milestone 2 onward, not bolted on at the end.

**Deliverables:**
- Consent flow audit: confirm consent is captured, timestamped, and stored against the upload record, not just displayed.
- Private storage audit: confirm no public S3 ACLs, all image access via short-expiry signed URLs, no image data in application logs.
- Secrets audit: confirm no AI/Stripe/DB keys in frontend bundles or committed to the repo; use a secrets manager (AWS Secrets Manager or SSM Parameter Store).
- Retention: implement the configurable retention window + scheduled deletion job (e.g. daily Lambda/cron) that purges S3 objects and DB rows past the window, and write the documented per-customer manual deletion runbook required by the brief.
- Content moderation review: confirm theme templates and instruction filtering actually block protected-IP terms (spot-check with adversarial test inputs like "Spider-Man," "Manchester United kit," etc.).
- UK GDPR pass: privacy policy content accuracy check, lawful basis documented (consent, for processing photos including of children), data processor agreement considerations for the AI provider and any sub-processors.
- Basic pen-test-lite pass before launch: auth bypass attempts on admin routes, IDOR checks (can order A's customer fetch order B's data?), file-upload content-type spoofing, webhook replay/signature-bypass attempts.

### 4.7 DevOps / Infrastructure Agent

**Scope:** everything needed to actually run this in production, reliably, under a real domain.

**Deliverables:**
- IaC (Terraform or AWS CDK) for RDS, S3 buckets (with correct private/CORS config for direct browser upload), ECS/Lambda, SQS/Redis, CloudFront + Route 53 for the client's domain, Secrets Manager entries.
- CI/CD pipeline (GitHub Actions): lint/test/build on PR, deploy to staging on merge to main, manual promote to production.
- Separate staging and production environments, with **Stripe test mode in staging and live mode only in production** per the brief's requirement.
- CloudWatch dashboards + alerts (5xx rate, generation-job failure rate, AI-spend threshold, queue backlog) and Sentry (or equivalent) error tracking wired into both frontend and backend.
- Backup/recovery: automated RDS snapshots, documented restore procedure, S3 versioning or equivalent on production-file buckets.
- Handover package: deployment instructions, all account access transferred/documented under the client's ownership, architecture doc, ongoing-cost estimate (AWS + AI provider + Stripe fees + email provider), migration notes if anything is provider-locked.

### 4.8 QA / Launch Agent

**Scope:** final gate before go-live, runs the Milestone 5 checklist.

**Deliverables:**
- Cross-device testing (mobile Safari/Chrome upload flow especially — mobile photo upload has historically been the flakiest part of flows like this).
- Full journey test: upload → generate → preview → regenerate (hit the cap) → approve → checkout → webhook → confirmation email → admin sees the order → admin downloads production file → admin marks statuses through to Dispatched.
- Failure-path testing: failed payment, failed generation (simulate provider timeout/error), webhook retry/duplicate delivery, expired signed URL.
- Security checklist sign-off (Section 4.6 items) before production DNS cutover.
- Domain connection, production smoke test, and a written post-launch support/bug-fix period agreement handed to the client.

---

## 5. Dependency / sequencing graph

```
Milestone 1 (POC — gates everything else)
  AI Pipeline Agent runs model bake-off on ≥5 real photos
  -> Orchestrator locks: AI provider, likeness approach, upscaler, bg-removal, cost/image
     ↓
Milestone 2 (parallel once stack is locked)
  Backend Agent: schema + core endpoints  ─┐
  Frontend Agent: upload/theme/instruction UI ─┤→ integrate on shared API contract
  DevOps Agent: staging env stood up        ─┘
     ↓
Milestone 3
  AI Pipeline Agent: production pipeline wired into Backend's async queue
  Payments/Abuse Agent: rate limits + moderation layer live
  Privacy/Security Agent: first audit pass
     ↓
Milestone 4
  Payments Agent: Stripe checkout + webhooks
  Admin Dashboard Agent: full CRUD + downloads + cost view
     ↓
Milestone 5
  QA Agent: full-journey + failure-path testing
  Privacy/Security Agent: final pass
  DevOps Agent: production cutover + handover package
```

---

## 6. Explicit answers to the brief's application questions (bake these into the build, don't leave them open)

- **AI model/API:** run the Milestone 1 bake-off (Section 2.2/4.3) between InstantID/PhotoMaker-class self-hosted-via-Replicate options and a fully managed provider; lock the winner in an ADR with the actual measured likeness/cost/latency numbers, not a guess made up front.
- **Facial identity preservation:** face-ID-conditioned image-to-image (InstantID/PhotoMaker/IP-Adapter FaceID style), not prompt-only text-to-image.
- **High-res production artwork:** generation output → dedicated upscaler → print-resolution PNG (target DPI confirmed with print vendor, documented in `/docs/architecture.md`).
- **Subject isolation/transparent background:** dedicated background-removal stage (rembg/BiRefNet or remove.bg/Clipdrop API), separate from the generation model.
- **Abuse/cost prevention:** email verification + IP/email rate limiting + hard free-generation caps + spend circuit breaker (Section 4.4); high-res file always payment-gated.
- **Photo protection/deletion:** private signed-URL storage, configurable retention job, admin manual delete, documented per-customer deletion runbook (Section 4.6).
- **Base44 vs. hybrid vs. rebuild:** rebuild on the conventional stack in Section 2.1 — full ownership, proper handling of private/child photos, and no platform lock-in for a product with custom async AI + payment flows.

---

## 7. Definition of Done (Orchestrator checks this before declaring the MVP launch-ready)

### 7.1 Customer journey
- [ ] Theme selection → upload → consent → optional instructions → generation → watermarked preview → approve/regenerate (capped) → size/options → delivery details → Stripe payment → confirmation page → confirmation email, all working end-to-end on staging with a real test photo.
- [ ] Mobile upload verified on at least iOS Safari and Android Chrome.
- [ ] Clear, non-technical error messaging on every failure path (upload rejected, generation failed, payment failed).

### 7.2 AI pipeline
- [ ] Image-to-image only; likeness preserved and reviewed against real test photos, not just demo images.
- [ ] No named/branded IP in any live theme template; instruction moderation actually blocks a tested adversarial input list.
- [ ] Preview (watermarked, low-res) and production (full-res, upscaled, bg-processed) artifacts are distinct and correctly linked to the order.
- [ ] Cost-per-generation measured and logged; visible on the admin cost dashboard.

### 7.3 Admin
- [ ] Every checklist item in Section 4.5 present and functional, including a real signed-URL production-file download and a real deletion action that removes S3 objects.

### 7.4 Payments
- [ ] Live Stripe webhook signature verification confirmed (not just tested against Stripe's local CLI in isolation — verify signing secret is the production one before cutover).
- [ ] Duplicate-order and duplicate-webhook handling verified.
- [ ] Refund flow tested against a real (test-mode) Stripe refund.

### 7.5 Security & privacy
- [ ] No secrets in frontend bundle or git history.
- [ ] All image storage private, signed-URL-only, verified by attempting an unauthenticated direct S3 fetch and confirming it fails.
- [ ] Admin routes reject unauthenticated/unauthorized access (tested, not assumed).
- [ ] IDOR check passed: one customer's order ID cannot retrieve another's data.
- [ ] Retention/deletion job runs and actually deletes on a test record past the retention window.
- [ ] Privacy policy and consent copy reviewed for accuracy against what the system actually does.

### 7.6 Infra & handover
- [ ] Staging and production environments both live, domain connected, HTTPS enforced.
- [ ] Monitoring/alerting live (error tracker + at least one AI-spend and one 5xx alert).
- [ ] Backups configured and a restore has been test-run at least once.
- [ ] Client has been handed: GitHub repo access, AWS account access, Stripe account access, AI provider account access, deployment docs, architecture docs, ongoing-cost estimate, and a written post-launch support-period agreement.

---

## 8. What's explicitly out of scope for this MVP (do not gold-plate)

Training a custom model, native mobile apps, multi-currency/international shipping, full print-machine automation, advanced customer accounts/loyalty, a large theme library, marketplace features. Keep the build disciplined to what's above — the brief is explicit that scope creep here is not wanted for phase one.
