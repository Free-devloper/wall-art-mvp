"""Celery worker for the AI image generation pipeline.

Runs the full 7-stage pipeline asynchronously:
1. Load records from DB
2. Download original photo from storage
3. AI identity-preserving generation (Replicate API or dev placeholder)
4. Background removal (rembg)
5. Upscale to print resolution
6. Create watermarked preview
7. Upload artifacts to storage + update DB
"""

import asyncio
import io
import logging
import time
import uuid
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.generation import Generation
from app.models.order import Order
from app.models.theme import Theme
from app.models.upload import Upload
from app.services.s3_service import storage_service
from app.services.circuit_breaker import CircuitBreaker
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


async def async_run_pipeline(generation_id: str):
    start_time = time.time()

    async with AsyncSessionLocal() as db:
        # --- Stage 1: Load records ---
        gen = await db.scalar(
            select(Generation).where(Generation.id == uuid.UUID(generation_id))
        )
        if not gen:
            logger.error(f"Generation {generation_id} not found")
            return

        try:
            gen.status = "processing"
            await db.commit()

            upload = await db.scalar(select(Upload).where(Upload.id == gen.upload_id))
            theme = await db.scalar(select(Theme).where(Theme.id == gen.theme_id))

            if not upload or not theme:
                raise ValueError("Upload or theme not found for this generation")

            # --- Stage 2: Download original photo ---
            try:
                original_bytes = storage_service.download_bytes(upload.s3_key_original)
                original_image = Image.open(io.BytesIO(original_bytes))
                logger.info(
                    f"Downloaded original: {upload.s3_key_original} "
                    f"({original_image.size[0]}x{original_image.size[1]})"
                )
            except FileNotFoundError:
                logger.warning(
                    f"Original file not found at {upload.s3_key_original}, "
                    "creating placeholder image for dev"
                )
                original_image = Image.new("RGB", (1024, 1024), color=(200, 200, 220))

            # --- Stage 3: AI generation ---
            # In dev mode (placeholder token), create a styled placeholder.
            # In production, call Replicate API with identity-preserving model.
            if settings.REPLICATE_API_TOKEN.startswith("r8_placeholder"):
                logger.info("Dev mode: generating placeholder artwork")
                generated = _create_dev_placeholder(original_image, theme, gen)
            else:
                generated = await _call_replicate(original_image, theme, gen)

            # --- Stage 4: Background removal (production only) ---
            # Skip in dev mode — rembg downloads a 1GB ONNX model and needs
            # significant RAM, which causes OOM kills in Docker dev containers.
            is_dev = settings.REPLICATE_API_TOKEN.startswith("r8_placeholder")
            if not is_dev:
                try:
                    import rembg

                    gen_bytes = io.BytesIO()
                    generated.save(gen_bytes, format="PNG")
                    removed = rembg.remove(gen_bytes.getvalue())
                    generated = Image.open(io.BytesIO(removed)).convert("RGBA")
                    logger.info("Background removed successfully")
                except Exception as e:
                    logger.warning(f"Background removal failed, keeping original: {e}")
            else:
                logger.info("Dev mode: skipping background removal")

            # --- Stage 5: Upscale to print resolution (production only) ---
            target_width = 4096
            if not is_dev and generated.width < target_width:
                scale = target_width / generated.width
                new_size = (target_width, int(generated.height * scale))
                generated = generated.resize(new_size, Image.LANCZOS)
                logger.info(f"Upscaled to {generated.size}")

            # --- Stage 6: Create watermarked preview ---
            preview = generated.copy()
            preview.thumbnail((1200, 1200), Image.LANCZOS)
            preview_rgb = preview.convert("RGB")
            _add_watermark(preview_rgb)

            # --- Stage 7: Upload artifacts to storage ---
            timestamp_str = datetime.now(timezone.utc).strftime("%Y/%m/%d")
            order_prefix = str(gen.order_id)[:8]

            # Production file (full-res PNG with transparency)
            prod_buffer = io.BytesIO()
            generated.save(prod_buffer, format="PNG", optimize=True)
            prod_bytes = prod_buffer.getvalue()
            s3_key_prod = f"generations/{timestamp_str}/{order_prefix}/{gen.id}_production.png"
            storage_service.upload_bytes(s3_key_prod, prod_bytes, "image/png")

            # Preview file (watermarked, lower-res JPEG)
            prev_buffer = io.BytesIO()
            preview_rgb.save(prev_buffer, format="JPEG", quality=85)
            prev_bytes = prev_buffer.getvalue()
            s3_key_prev = f"generations/{timestamp_str}/{order_prefix}/{gen.id}_preview.jpg"
            storage_service.upload_bytes(s3_key_prev, prev_bytes, "image/jpeg")

            # Update generation record
            gen.s3_key_production = s3_key_prod
            gen.s3_key_preview = s3_key_prev
            gen.status = "completed"
            gen.completed_at = datetime.utcnow()
            gen.generation_time_ms = int((time.time() - start_time) * 1000)

            # Record cost
            cost = 0.05 if settings.REPLICATE_API_TOKEN.startswith("r8_placeholder") else 0.10
            gen.cost_usd = cost
            CircuitBreaker.record_spend(cost)

            await db.commit()
            
            # Send generation complete email
            try:
                from app.services.email_service import EmailService
                order_result = await db.execute(select(Order).where(Order.id == gen.order_id))
                order = order_result.scalar_one_or_none()
                if order and order.customer_email:
                    await EmailService.send_generation_complete(order)
                    logger.info(f"Generation complete email sent to {order.customer_email}")
            except Exception as email_err:
                logger.warning(f"Failed to send generation complete email: {email_err}")

            logger.info(
                f"Generation {generation_id} completed in {gen.generation_time_ms}ms "
                f"(cost=${cost:.2f})"
            )

        except Exception as e:
            logger.error(f"Generation pipeline failed for {generation_id}: {e}", exc_info=True)
            gen.status = "failed"
            gen.failure_reason = str(e)[:500]
            await db.commit()


def _create_dev_placeholder(
    original: Image.Image, theme, gen
) -> Image.Image:
    """Create a styled placeholder image for dev/testing without calling AI."""
    img = Image.new("RGB", (1024, 1024), color=(45, 55, 72))
    draw = ImageDraw.Draw(img)

    # Paste a thumbnail of the original in the centre
    thumb = original.copy()
    thumb.thumbnail((400, 400), Image.LANCZOS)
    paste_x = (1024 - thumb.width) // 2
    paste_y = (1024 - thumb.height) // 2
    img.paste(thumb, (paste_x, paste_y))

    # Add theme name overlay
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    except (IOError, OSError):
        font = ImageFont.load_default()

    theme_name = theme.name if theme else "Unknown Theme"
    draw.text((50, 50), f"Theme: {theme_name}", fill="white", font=font)
    draw.text((50, 950), "[DEV PLACEHOLDER]", fill=(255, 200, 50), font=font)

    if gen.instructions_text:
        draw.text(
            (50, 100),
            f"Instructions: {gen.instructions_text[:80]}",
            fill=(200, 200, 200),
        )

    return img


async def _call_replicate(original: Image.Image, theme, gen) -> Image.Image:
    """Call the Replicate API for identity-preserving image generation."""
    import httpx

    # Convert original to base64 for API
    import base64

    buffer = io.BytesIO()
    original.save(buffer, format="JPEG", quality=90)
    image_b64 = base64.b64encode(buffer.getvalue()).decode()

    prompt = theme.prompt_template
    if gen.instructions_text:
        prompt += f"\nAdditional instructions: {gen.instructions_text}"

    async with httpx.AsyncClient(timeout=120) as client:
        # Start prediction
        response = await client.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {settings.REPLICATE_API_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "version": "your-model-version-here",
                "input": {
                    "image": f"data:image/jpeg;base64,{image_b64}",
                    "prompt": prompt,
                },
            },
        )
        response.raise_for_status()
        prediction = response.json()

        # Poll for completion
        prediction_url = prediction.get("urls", {}).get("get", "")
        for _ in range(60):  # Max 5 minutes
            await asyncio.sleep(5)
            poll = await client.get(
                prediction_url,
                headers={"Authorization": f"Token {settings.REPLICATE_API_TOKEN}"},
            )
            poll.raise_for_status()
            result = poll.json()

            if result["status"] == "succeeded":
                output_url = result["output"]
                if isinstance(output_url, list):
                    output_url = output_url[0]
                img_response = await client.get(output_url)
                return Image.open(io.BytesIO(img_response.content))

            if result["status"] == "failed":
                raise RuntimeError(f"Replicate prediction failed: {result.get('error')}")

        raise TimeoutError("Replicate prediction timed out after 5 minutes")


def _add_watermark(image: Image.Image):
    """Add diagonal 'PREVIEW' watermark text across the image."""
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    except (IOError, OSError):
        font = ImageFont.load_default()

    # Draw semi-transparent PREVIEW text diagonally across the image
    w, h = image.size
    for y in range(0, h, 200):
        for x in range(-200, w, 400):
            draw.text(
                (x, y),
                "PREVIEW",
                fill=(255, 255, 255, 80) if image.mode == "RGBA" else (200, 200, 200),
                font=font,
            )


@celery_app.task(
    name="app.workers.generation_worker.run_generation_pipeline",
    bind=True,
    max_retries=2,
)
def run_generation_pipeline(self, generation_id: str):
    """Celery entry point — runs the async pipeline."""
    try:
        asyncio.run(async_run_pipeline(generation_id))
    except Exception as exc:
        logger.error(f"Generation task failed (attempt {self.request.retries + 1}): {exc}")
        raise self.retry(exc=exc, countdown=2 ** (self.request.retries + 1))
