from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.services.stripe_service import StripeService
from app.models.order import Order
from app.services.email_service import EmailService

router = APIRouter()
email_service = EmailService()


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = StripeService.verify_webhook_signature(payload, sig_header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        order_id = StripeService.process_checkout_completed(event)
        if order_id:
            order = await db.scalar(select(Order).where(Order.id == order_id))
            if order and order.status != "paid":
                order.status = "paid"
                order.stripe_payment_id = event["data"]["object"].get("payment_intent")
                await db.commit()
                # Send confirmation email
                await email_service.send_order_confirmation(order)
    elif event["type"] == "payment_intent.payment_failed":
        obj = event["data"]["object"]
        order_id = obj.get("metadata", {}).get("order_id")
        if order_id:
            order = await db.scalar(select(Order).where(Order.id == order_id))
            if order:
                order.status = "payment_failed"
                await db.commit()
    elif event["type"] == "charge.refunded":
        obj = event["data"]["object"]
        payment_intent = obj.get("payment_intent")
        if payment_intent:
            order = await db.scalar(select(Order).where(Order.stripe_payment_id == payment_intent))
            if order:
                order.status = "refunded"
                await db.commit()

    return {"status": "success"}
