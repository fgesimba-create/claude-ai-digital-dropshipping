"""Stripe payment processing service."""
import stripe
import structlog
from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()

stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Handles all Stripe payment operations."""

    async def create_payment_intent(
        self,
        amount_cents: int,
        currency: str = "usd",
        metadata: dict = None,
    ) -> dict:
        """Create a Stripe PaymentIntent for checkout."""
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency,
            automatic_payment_methods={"enabled": True},
            metadata=metadata or {},
        )
        log.info("stripe.payment_intent_created", intent_id=intent.id, amount=amount_cents)
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
        }

    async def confirm_payment(self, payment_intent_id: str) -> dict:
        """Retrieve and verify a payment intent status."""
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {
            "id": intent.id,
            "status": intent.status,
            "amount": intent.amount,
            "currency": intent.currency,
            "charges": [
                {
                    "charge_id": charge.id,
                    "paid": charge.paid,
                }
                for charge in intent.charges.data
            ] if intent.charges.data else [],
        }

    async def create_refund(self, charge_id: str, amount_cents: int = None, reason: str = "requested_by_customer") -> dict:
        """Issue a full or partial refund."""
        params = {"charge": charge_id, "reason": reason}
        if amount_cents:
            params["amount"] = amount_cents

        refund = stripe.Refund.create(**params)
        log.info("stripe.refund_created", refund_id=refund.id, charge_id=charge_id)
        return {"refund_id": refund.id, "status": refund.status, "amount": refund.amount}

    def verify_webhook(self, payload: bytes, sig_header: str) -> dict:
        """Verify and parse a Stripe webhook event."""
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
        return event

    async def get_dashboard_metrics(self) -> dict:
        """Pull revenue metrics from Stripe for the analytics dashboard."""
        # Get last 30 days of charges
        import time
        since = int(time.time()) - (30 * 24 * 3600)
        charges = stripe.Charge.list(created={"gte": since}, limit=100)

        total_revenue = sum(c.amount for c in charges.data if c.paid) / 100
        total_refunded = sum(c.amount_refunded for c in charges.data) / 100

        return {
            "total_revenue_30d": total_revenue,
            "total_refunded_30d": total_refunded,
            "net_revenue_30d": total_revenue - total_refunded,
            "transaction_count": len([c for c in charges.data if c.paid]),
        }
