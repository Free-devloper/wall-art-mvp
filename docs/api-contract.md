# API Contract

This document defines the REST API contract for the Wall Art backend.

## Base URL
All endpoints are relative to `/api` (e.g., `https://api.wallart.com/api/`).

---

## Customer Endpoints

### `POST /api/themes`
List active themes.
- **Auth:** None
- **Request Body:** None
- **Response (200):**
  ```json
  [
    {
      "id": "theme_123",
      "name": "Astronaut",
      "description": "Space explorer suit",
      "preview_image_url": "https://..."
    }
  ]
  ```

### `POST /api/uploads`
Request a presigned URL to upload a photo directly to S3.
- **Auth:** None
- **Request Body:**
  ```json
  {
    "customer_email": "user@example.com",
    "consent_confirmed": true
  }
  ```
- **Response (200):**
  ```json
  {
    "upload_url": "https://s3.amazonaws.com/...",
    "upload_id": "up_123abc",
    "fields": {
      "key": "...",
      "AWSAccessKeyId": "...",
      "policy": "...",
      "signature": "..."
    }
  }
  ```

### `POST /api/orders`
Create a draft order.
- **Auth:** None
- **Request Body:**
  ```json
  {
    "theme_id": "theme_123",
    "upload_id": "up_123abc",
    "instructions": "Make the suit blue",
    "product_size": "medium",
    "customer_email": "user@example.com",
    "customer_name": "John Doe"
  }
  ```
- **Response (201):**
  ```json
  {
    "id": "order_456",
    "status": "draft",
    "theme_id": "theme_123",
    "created_at": "2024-01-01T12:00:00Z"
  }
  ```

### `POST /api/orders/{id}/generate`
Start the AI generation process.
- **Auth:** None (Rate limited by IP/Session)
- **Response (202):**
  ```json
  {
    "generation_id": "gen_789",
    "status": "processing"
  }
  ```

### `GET /api/orders/{id}/generation-status`
Poll status of the generation.
- **Auth:** None
- **Response (200):**
  ```json
  {
    "status": "completed",
    "preview_url": "https://s3... (signed)",
    "remaining_regenerations": 2
  }
  ```

### `POST /api/orders/{id}/regenerate`
Regenerate artwork.
- **Auth:** None
- **Request Body:**
  ```json
  {
    "reason": "Eyes look weird"
  }
  ```
- **Response (202):**
  ```json
  {
    "generation_id": "gen_790",
    "remaining": 1
  }
  ```

### `POST /api/orders/{id}/approve`
Approve the current preview.
- **Auth:** None
- **Response (200):** Order Object

### `POST /api/orders/{id}/checkout-session`
Create a Stripe checkout session.
- **Auth:** None
- **Request Body:**
  ```json
  {
    "success_url": "https://...",
    "cancel_url": "https://...",
    "shipping_address": { ... }
  }
  ```
- **Response (200):**
  ```json
  {
    "checkout_url": "https://checkout.stripe.com/...",
    "session_id": "cs_test_..."
  }
  ```

### `POST /api/webhooks/stripe`
Stripe webhook endpoint.
- **Auth:** Stripe Signature header
- **Response (200):** `{ "received": true }`

### `GET /api/orders/{id}/confirmation`
Get order confirmation data.
- **Auth:** None (Requires valid Order ID)
- **Response (200):** Order details including shipping status.

---

## Admin Endpoints

*All admin endpoints require `Authorization: Bearer <token>`.*

### `POST /api/admin/auth/login`
- **Request:** `{ "email": "admin@x.com", "password": "..." }`
- **Response:** `{ "token": "jwt...", "admin": { "name": "Admin" } }`

### `GET /api/admin/auth/me`
- **Response:** Admin user object.

### `GET /api/admin/orders`
List orders with pagination and filtering.
- **Query Params:** `status`, `theme`, `date_from`, `date_to`, `search`, `page`, `per_page`
- **Response:** Paginated list of Order objects.

### `GET /api/admin/orders/{id}`
Full order detail including hidden metadata.

### `POST /api/admin/orders/{id}/regenerate`
Admin override to regenerate without consuming customer credits.

### `POST /api/admin/orders/{id}/status`
Update order status manually.
- **Request:** `{ "status": "shipped", "production_notes": "..." }`

### `GET /api/admin/orders/{id}/production-file`
Get a signed download URL for the high-res production file.
- **Response:** `{ "url": "https://..." }`

### `DELETE /api/admin/orders/{id}/photos`
Hard delete all associated photos/generations from S3 (GDPR).
- **Response:** 204 No Content

### `GET /api/admin/costs`
Cost dashboard data aggregating API usage and AI spend.

### `GET /api/admin/themes`
List all themes (including inactive).

### `POST /api/admin/themes`
Create a new theme.

### `PATCH /api/admin/themes/{id}`
Update an existing theme (e.g., mark active/inactive).
