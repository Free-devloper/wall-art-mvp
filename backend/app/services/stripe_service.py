import stripe
from app.config import settings
from app.models.order import Order
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    @staticmethod
    def create_checkout_session(order: Order, success_url: str, cancel_url: str) -> stripe.checkout.Session:
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'gbp',
                        'unit_amount': order.price_cents,
                        'product_data': {
                            'name': f"Wall Art - {order.product_size}",
                            'description': "Custom AI generated artwork",
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(order.id),
                customer_email=order.customer_email,
                metadata={
                    'order_id': str(order.id)
                }
            )
            return session
        except Exception as e:
            logger.error(f"Error creating stripe checkout session: {e}")
            raise

    @staticmethod
    def verify_webhook_signature(payload: bytes, sig_header: str) -> stripe.Event:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except stripe.error.SignatureVerificationError as e:
            raise ValueError("Invalid signature")
        except ValueError as e:
            raise ValueError("Invalid payload")

    @staticmethod
    def process_checkout_completed(event: stripe.Event) -> str | None:
        session = event['data']['object']
        order_id = session.get('client_reference_id')
        if not order_id:
            order_id = session.get('metadata', {}).get('order_id')
        return order_id
        
    @staticmethod
    def create_refund(payment_intent_id: str, amount_cents: int) -> stripe.Refund:
        return stripe.Refund.create(
            payment_intent=payment_intent_id,
            amount=amount_cents
        )
