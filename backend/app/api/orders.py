from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, CheckoutSessionResponse, OrderConfirmation
from app.schemas.generation import GenerationStatusResponse, GenerateRequest, RegenerateRequest
from app.models.order import Order
from app.models.theme import Theme
from app.models.upload import Upload
from app.models.regeneration_log import RegenerationLog
from app.services.generation_service import GenerationService
from app.services.moderation_service import ModerationService
from app.services.stripe_service import StripeService
from app.services.circuit_breaker import CircuitBreaker
from app.services.rate_limiter import RateLimiter
from app.config import settings
from app.auth.clerk import get_clerk_user, ClerkUser

router = APIRouter()


@router.post("", response_model=OrderResponse)
async def create_order(
    order_req: OrderCreate, db: AsyncSession = Depends(get_db), user: ClerkUser = Depends(get_clerk_user)
):
    theme = await db.scalar(select(Theme).where(Theme.id == order_req.theme_id))
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")

    upload = await db.scalar(select(Upload).where(Upload.id == order_req.upload_id))
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    if order_req.instructions:
        is_clean, _ = ModerationService.check_instructions(order_req.instructions)
        if not is_clean:
            raise HTTPException(status_code=400, detail="Instructions contain blocked terms")

    order = Order(
        user_id=user.user_id,
        theme_id=theme.id,
        product_size=order_req.product_size,
        price_cents=theme.price_cents,
        customer_email=order_req.customer_email or user.email,
        customer_name=order_req.customer_name or user.name or "Customer",
        status="new",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    upload.order_id = order.id
    await db.commit()

    return order


@router.post("/{id}/generate")
async def generate_order(id: uuid.UUID, req: GenerateRequest, request: Request, db: AsyncSession = Depends(get_db)):
    order = await db.scalar(select(Order).where(Order.id == id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    client_ip = request.client.host if request.client else "unknown"
    allowed, _, _ = RateLimiter.check_rate_limit(f"gen:{client_ip}", 10, 3600)
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    budget_ok, _, _ = CircuitBreaker.check_budget()
    if not budget_ok:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable (Budget limit reached)")

    upload = await db.scalar(select(Upload).where(Upload.order_id == id))
    if not upload:
        raise HTTPException(status_code=400, detail="No upload linked to order")

    instructions = req.instructions if req.instructions else ""
    if instructions:
        instructions = ModerationService.sanitize_instructions(instructions)

    await GenerationService.enqueue_generation(db, order.id, upload.id, order.theme_id, instructions)

    return {"message": "Generation queued"}


@router.get("/{id}/generation-status", response_model=GenerationStatusResponse)
async def get_generation_status(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await GenerationService.get_generation_status(db, id)


@router.post("/{id}/regenerate")
async def regenerate_order(id: uuid.UUID, req: RegenerateRequest, db: AsyncSession = Depends(get_db)):
    can_regen = await GenerationService.can_regenerate(db, id)
    if not can_regen:
        raise HTTPException(status_code=400, detail="Maximum regenerations reached")

    order = await db.scalar(select(Order).where(Order.id == id))
    upload = await db.scalar(select(Upload).where(Upload.order_id == id))

    from app.models.generation import Generation

    # Get the last generation
    last_gen_result = await db.execute(
        select(Generation).where(Generation.order_id == id).order_by(Generation.created_at.desc()).limit(1)
    )
    last_gen = last_gen_result.scalar_one_or_none()

    regen_log = RegenerationLog(
        order_id=id,
        generation_id=last_gen.id if last_gen else None,
        reason=req.reason if hasattr(req, "reason") else "",
    )
    db.add(regen_log)

    await GenerationService.enqueue_generation(
        db, order.id, upload.id, order.theme_id, req.reason if hasattr(req, "reason") else ""
    )

    return {"message": "Regeneration queued"}


@router.post("/{id}/approve")
async def approve_order(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    order = await db.scalar(select(Order).where(Order.id == id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = "approved"
    await db.commit()
    return {"message": "Approved"}


@router.post("/{id}/checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    order = await db.scalar(select(Order).where(Order.id == id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Dev mode: skip Stripe, go straight to confirmation
    if "placeholder" in settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == "":
        order.status = "paid"
        order.stripe_checkout_session_id = f"dev_session_{order.id}"
        await db.commit()
        return CheckoutSessionResponse(checkout_url=f"{settings.FRONTEND_URL}/order/{id}/confirmation")

    success_url = f"{settings.FRONTEND_URL}/order/{id}/confirmation"
    cancel_url = f"{settings.FRONTEND_URL}/order/{id}/options"

    session = StripeService.create_checkout_session(order, success_url, cancel_url)
    order.stripe_checkout_session_id = session.id
    await db.commit()

    return CheckoutSessionResponse(checkout_url=session.url)


@router.get("/{id}/confirmation", response_model=OrderConfirmation)
async def get_confirmation(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    order = await db.scalar(select(Order).where(Order.id == id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return OrderConfirmation(
        order_id=order.id, status=order.status, customer_email=order.customer_email, total_cents=order.price_cents
    )
