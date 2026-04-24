"""
Stripe webhook handler — processes payment events automatically.
Payment succeeded → order fulfillment triggered immediately.
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.stripe_service import StripeService
from app.services.order_service import OrderService
import structlog

log = structlog.get_logger()
router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Handle Stripe webhook events.
    payment_intent.succeeded → auto-fulfill order with supplier.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    stripe_service = StripeService()
    try:
        event = stripe_service.verify_webhook(payload, sig_header)
    except ValueError as e:
        log.warning("webhook.invalid_payload", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        log.warning("webhook.signature_invalid", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    log.info("webhook.received", event_type=event_type)

    if event_type == "payment_intent.succeeded":
        pi = event["data"]["object"]
        payment_intent_id = pi["id"]
        charge_id = pi.get("latest_charge", "")

        order_service = OrderService(db)
        order = await order_service.mark_payment_confirmed(payment_intent_id, charge_id)

        if order:
            log.info("webhook.payment_confirmed", order_number=order.order_number)
            await order_service.fulfill_order(order.id)
        else:
            log.warning("webhook.order_not_found", payment_intent_id=payment_intent_id)

    elif event_type == "payment_intent.payment_failed":
        pi = event["data"]["object"]
        log.warning("webhook.payment_failed", payment_intent_id=pi["id"])

    elif event_type == "charge.refunded":
        charge = event["data"]["object"]
        log.info("webhook.refund_processed", charge_id=charge["id"])

    return {"status": "ok"}
