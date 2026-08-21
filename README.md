# 🎨 WallArt MVP — AI-Powered Custom Vinyl Wall Graphics Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?style=flat&logo=TypeScript&logoColor=white)](https://www.typescriptlang.org/)
[![Clerk Auth](https://img.shields.io/badge/Clerk-Authentication-6C47FF.svg?style=flat&logo=Clerk&logoColor=white)](https://clerk.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-38B2AC.svg?style=flat&logo=TailwindCSS&logoColor=white)](https://tailwindcss.com/)
[![Celery](https://img.shields.io/badge/Celery-5.3+-37814A.svg?style=flat&logo=Celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=Docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?style=flat&logo=PostgreSQL&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D.svg?style=flat&logo=Redis&logoColor=white)](https://redis.io/)
[![Stripe](https://img.shields.io/badge/Stripe-Checkout-635BFF.svg?style=flat&logo=Stripe&logoColor=white)](https://stripe.com/)

An end-to-end full-stack SaaS and e-commerce platform that transforms everyday customer photos into personalized, AI-stylized wall art graphics (e.g. Astronauts, Fantasy Watercolor, Anime, Cyberpunk, Oil Paintings), prepares print-ready 4K 300 DPI vinyl graphics, and automates physical fulfillment.

---

## 📌 Repository Summary

* **Short Description:** Full-stack AI SaaS platform for generating, previewing, and ordering custom vinyl wall art from personal photos with FastAPI, React, Celery, Clerk & Stripe.
* **Topics/Tags:** `fastapi`, `react`, `typescript`, `ai-art`, `stable-diffusion`, `clerk-auth`, `celery`, `redis`, `docker`, `stripe-checkout`, `saas`, `tailwind-css`, `wall-art`, `rembg`, `pillow`, `print-on-demand`

---

## 📖 Table of Contents
1. [WHAT is WallArt?](#-what-is-wallart)
2. [WHY WallArt? (Problem & Tech Rationale)](#-why-wallart)
3. [WHERE is Everything? (Architecture & Codebase Map)](#-where-is-everything)
4. [HOW to Run (Quickstart Guide)](#-how-to-run)
5. [🛡️ SaaS & Security Features](#️-saas--security-features)
6. [📊 Business & Unit Economics](#-business--unit-economics)

---

## 🎯 WHAT is WallArt?

WallArt automates the entire consumer-to-print pipeline for personalized AI art:

### Customer Experience:
1. **Browse Gallery**: Explore curated visual styles (Cyberpunk, Superhero, Renaissance, Pixar 3D, Anime, Watercolor).
2. **One-Click Auth**: Seamless authentication via **Clerk** (Google, Email, Socials).
3. **Upload Photo & Consent**: Fast client-side image validation and GDPR consent declaration.
4. **Asynchronous 7-Stage AI Pipeline**:
   - Original image quality validation & S3 ingestion.
   - Diffusion-based stylization (Replicate / Fine-tuned SDXL).
   - Automated background isolation using `rembg`.
   - Ultra-high-resolution 4096px print upscaling via Lanczos resampling.
   - Diagonal `PREVIEW` watermarked preview generation.
5. **Instant Live Progress**: Real-time stage tracking with custom-branded animations.
6. **Preview & Approval / Regeneration**: Inspect artwork, approve preview, or request prompt-guided regenerations (up to theme cap).
7. **Size & Options Selection**: Choose standard print sizes (A3, A2, A1, A0, 50x70cm, 70x100cm) with dynamic pricing in GBP/USD.
8. **Stripe Checkout**: Embedded Stripe payment session with address collection and instant automated email confirmations.

### Admin Management Portal (`/admin`):
* **Order Operations**: Full list with status filtering (`new`, `paid`, `in_production`, `shipped`, `delivered`, `cancelled`), customer address viewing, and status transitions.
* **Production File Center**: 1-click generation and download of 300 DPI uncompressed high-res production assets for physical vinyl printing.
* **Manual Overrides**: Admin manual re-generation trigger and GDPR data deletion action.
* **Theme Management (CRUD)**: Create, edit, activate/deactivate, re-order, and price styles directly from UI.
* **AI Cost & Spend Analytics**: Real-time tracking of daily/monthly spend, per-generation averages, 30-day volume charts, and per-theme spend breakdown.
* **User Management**: View customer accounts, aggregate order histories, and lifetime spend.

---

## 💡 WHY WallArt?

### 1. Market Opportunity & Problem
Custom wall prints and personalized gifts are a multi-billion dollar market, but traditional custom portraiture is expensive (£50–£200) and takes 3–7 business days of human artist time. WallArt delivers **personalized high-end wall art in under 15 seconds** at a fraction of the cost.

### 2. Technical Decisions
* **FastAPI (Python 3.12)**: Native async I/O handles high-throughput web traffic, webhooks, and presigned S3 orchestration without event-loop blocking.
* **Celery + Redis**: Decouples long-running AI compute (10–15s) from HTTP request cycles, allowing horizontal scaling of GPU/CPU workers.
* **Clerk Auth**: Enterprise-grade customer identity, session management, and social logins with zero database maintenance overhead.
* **Dual Storage Engine**: Zero-setup local filesystem storage for local Docker development + AWS S3 for staging and production.
* **Safety Circuit Breaker**: Real-time Redis spend tracking enforces daily ($50–$500) and monthly safety ceilings to prevent budget overruns.

---

## 🗺️ WHERE is Everything?

### Architecture Diagram
```
                     [ Client Browser / Mobile ]
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
        [ React 18 + Vite SPA ]         [ Clerk Auth ]
       (Port 5173 / Tailwind / HMR)    (JWT Identity)
                   │
                   ▼ (Reverse Proxy / API Requests)
       ┌───────────────────────────────────────────────┐
       │             FastAPI Backend (Port 8000)        │
       │  • Router: /themes, /uploads, /orders, /admin │
       │  • Security: Rate Limiting & Clerk JWT JWKS   │
       │  • CORS & Global Exception Middleware        │
       └───────┬──────────────┬────────────────┬───────┘
               │              │                │
               ▼              ▼                ▼
     [ PostgreSQL 16 ]  [ Redis Broker ]  [ Local / S3 Storage ]
      • Orders           • Task Queue       • Uploads (Original)
      • Themes           • Rate Limits      • Previews (Watermarked)
      • Audit Logs       • Spend Caps       • Production (4K PNG)
      • Admin Users            │
                               ▼
               ┌───────────────────────────────┐
               │    Celery Worker Pipeline     │
               │  1. Replicate AI Model        │
               │  2. rembg Background Removal  │
               │  3. 4096px Lanczos Upscale    │
               │  4. Watermark & Spend Logger  │
               │  5. Email Notification        │
               └───────────────────────────────┘
```

### Directory Structure Map
```
wallArt/
├── backend/                        # FastAPI Application & Workers
│   ├── app/
│   │   ├── api/                    # REST Endpoints
│   │   │   ├── admin/              # Admin CRUD (Themes, Orders, Costs, Users)
│   │   │   ├── orders.py           # Customer Order & Generation Flow
│   │   │   ├── uploads.py          # Presigned Image Upload Endpoints
│   │   │   ├── themes.py           # Public Theme Gallery API
│   │   │   ├── webhooks.py         # Stripe Webhook Listeners
│   │   │   └── local_storage.py    # Local Storage Emulation for Dev
│   │   ├── auth/                   # Authentication Providers (JWT + Clerk JWKS)
│   │   ├── models/                 # SQLAlchemy 2.0 Async Models
│   │   ├── schemas/                # Pydantic v2 Request/Response Schemas
│   │   ├── services/               # Core Services (AI, Stripe, S3, Email, Circuit Breaker)
│   │   └── workers/                # Celery Background Tasks & Retention Cron
│   ├── Dockerfile                  # Python 3.12 Multi-Stage Dockerfile
│   └── requirements.txt            # Python Dependencies
│
├── frontend/                       # React 18 + TypeScript + Vite Client
│   ├── src/
│   │   ├── components/             # Reusable UI (Branded Spinner, Navbar, FileUploader)
│   │   ├── lib/                    # Axios Client, Auth Interceptors, Utilities
│   │   ├── pages/                  # Customer Pages (Home, Gallery, Upload, Preview, Checkout)
│   │   │   └── admin/              # Admin Dashboard (Orders, Detail, Themes, Costs, Users)
│   │   ├── types/                  # TypeScript Data Contracts
│   │   └── App.tsx                 # React Router v6 & Protected Routes
│   ├── Dockerfile                  # Node 20 Dev & Build Container
│   └── vite.config.ts              # Vite Config with HMR & Backend Proxy
│
├── infra/                          # Infrastructure as Code
│   └── terraform/                  # AWS ECS, RDS, S3, CloudFront Terraform Config
├── docs/                           # Architecture, API Contracts & ADR Docs
└── docker-compose.yml              # Complete Multi-Container Local Dev Stack
```

---

## 🚀 HOW to Run

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with WSL2 on Windows or native Docker on Mac/Linux)

### 1. Start the Complete Stack with Docker
```bash
# Clone the repository
git clone git@github.com:Free-devloper/wall-art-mvp.git
cd wall-art-mvp

# Start all 6 services with hot-reload enabled
docker-compose up -d
```

### 2. Access the Applications
| Service | URL | Credentials / Notes |
|---|---|---|
| **Customer Storefront** | [http://localhost:5173](http://localhost:5173) | Sign in with Clerk or browse themes |
| **Admin Dashboard** | [http://localhost:5173/admin](http://localhost:5173/admin) | `admin@wallart.co.uk` / `admin123dev` |
| **FastAPI Swagger Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API Explorer |
| **PostgreSQL Database** | `localhost:5432` | `wallart` / `wallart_dev_password` |
| **Redis Cache & Queue** | `localhost:6379` | Default DB 0 |

---

## 🛡️ SaaS & Security Features

* **Strict Content & IP Moderation**: Rejects and sanitizes trademarked/copyrighted terms (Disney, Marvel, Premier League clubs, luxury fashion) and NSFW input.
* **Spend Circuit Breaker**: Automatically pauses AI generations if daily ($50) or monthly ($1,000) spend ceilings are hit.
* **Rate Limiting Protection**: Redis sliding window limits on image uploads (5/hr) and generation requests (10/hr) per IP.
* **GDPR Compliance & Retention Worker**: Celery Beat scheduled daily task purges uploaded images older than 90 days and redacts PII.
* **Audit Logging**: Every admin action (status transition, high-resolution file download, manual photo purge) is recorded in immutable `audit_logs`.

---

## 📊 Business & Unit Economics

```
Average Retail Price (A2/A1 Print):  £39.99 (~$50.00 USD)
AI Model Compute Cost:               ~$0.05 – $0.10
Physical Print & Framing Cost:       ~$14.00 – $18.00
Payment Processing (Stripe 2.9%):    ~$1.75
---------------------------------------------------------
Estimated Gross Profit per Order:    ~$30.00 (60% – 70% Net Margin)
```

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
