# Architecture Decision Records (ADR)

## ADR-001: Stack Selection
- **Context:** The platform requires full control over asynchronous AI pipelines, secure private photo storage, and custom payment flows.
- **Decision:** Conventional stack (React+Vite+Tailwind frontend, FastAPI backend, PostgreSQL, Redis+Celery) over Base44 or other no-code tools.
- **Rationale:** Custom async AI and payment flows need full backend control. Security for customer photos (especially children) is paramount. The client owns all code without platform lock-in.

## ADR-002: AI Provider - Replicate as Primary
- **Context:** Need robust, identity-preserving image-to-image generation capabilities.
- **Decision:** Use Replicate API with InstantID/PhotoMaker models, abstracted behind an internal provider interface.
- **Rationale:** Pay-per-use model scales well for MVP. No infrastructure to manage for GPUs. Good model selection available.
- **Status:** Pending Milestone 1 bake-off validation to finalize model selection.

## ADR-003: Generation Gating - Free Preview with Rate Limits
- **Context:** Need to balance conversion rates (low friction preview) against abuse prevention.
- **Decision:** Free preview generation gated by email + IP rate limiting + hard cap per session. High-res production files are always gated behind a successful payment.
- **Rationale:** Preserves the low-friction 'preview before you buy' journey as requested in the project brief.

## ADR-004: Admin Auth - JWT with Email/Password
- **Context:** The admin dashboard needs authentication.
- **Decision:** Simple custom JWT auth with email/password for MVP.
- **Rationale:** Simple to implement quickly; avoids external auth provider dependency and costs for the MVP phase.

## ADR-005: Frontend Architecture - Single SPA with Protected Admin Routes
- **Context:** Admin dashboard could be a separate application or integrated into the main storefront app.
- **Decision:** Single React SPA. Admin routes are placed under `/admin` and protected by auth guards.
- **Rationale:** Simpler deployment, shared UI components, and a single build pipeline reduce maintenance overhead.

## ADR-006: Storage - Private S3 with Signed URLs
- **Context:** Customer photos need strict privacy guarantees.
- **Decision:** All S3 buckets are private with `BlockPublicAccess=True`. All file access is via 15-minute temporary signed URLs.
- **Rationale:** Ensures UK GDPR compliance and aligns with the brief's requirement for secure private storage.

## ADR-007: Background Removal - rembg Self-Hosted
- **Context:** AI generation often includes unwanted background artifacts. We need clean alpha channel separation for print.
- **Decision:** Use the `rembg` library (BiRefNet model) run locally inside the Celery worker.
- **Rationale:** Zero API cost, good quality, and eliminates the latency/privacy concerns of sending data to a third-party background removal service.
