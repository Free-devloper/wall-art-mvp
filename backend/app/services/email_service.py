import httpx
import logging
from app.config import settings
from app.models.order import Order

logger = logging.getLogger(__name__)


class EmailService:
    @classmethod
    async def send_email(cls, to_email: str, subject: str, html: str) -> bool:
        api_key = settings.RESEND_API_KEY
        from_email = settings.EMAIL_FROM
        if not api_key or api_key.startswith("re_") or "placeholder" in api_key:
            logger.info(f"[EMAIL MOCK] To: {to_email} | Subject: {subject} | HTML length: {len(html)}")
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"from": from_email, "to": [to_email], "subject": subject, "html": html},
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    @classmethod
    async def send_order_confirmation(cls, order: Order) -> bool:
        subject = f"Order Confirmation - {order.id}"
        html = f"<h1>Thank you for your order!</h1><p>Your order ID is {order.id}. We are working on your custom wall art.</p>"
        return await cls.send_email(order.customer_email, subject, html)

    @classmethod
    async def send_generation_complete(cls, order: Order) -> bool:
        subject = "Your Wall Art is Ready for Review!"
        html = f"<h1>Great news!</h1><p>Your generation for order {order.id} is ready. Please log in to approve or request a regeneration.</p>"
        return await cls.send_email(order.customer_email, subject, html)
