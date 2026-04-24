"""Order creation and checkout API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_db
from app.services.order_service import OrderService
from app.services.stripe_service import StripeService
import structlog

log = structlog.get_logger()
router = APIRouter()


class ShippingAddress(BaseModel):
    line1: str
    line2: Optional[str] = ""
    city: str
    state: str
    zip: str
    country: str = "United States"
    country_code: str = "US"


class CheckoutItem(BaseModel):
    product_id: str
    quantity: int


class CreateCheckoutSession(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None
    shipping_address: ShippingAddress
    items: list[CheckoutItem]


class ConfirmOrder(BaseModel):
    payment_intent_id: str
    checkout_data: CreateCheckoutSession


@router.post("/create-payment-intent")
async def create_payment_intent(
    checkout: CreateCheckoutSession,
    db: AsyncSession = Depends(get_db),
):
    """
    Step 1 of checkout: calculate total and create a Stripe PaymentIntent.
    Frontend uses the client_secret to collect payment details with Stripe.js.
    """
    from app.models.product import Product

    # Validate items and calculate total
    subtotal = 0.0
    items_detail = []
    for item in checkout.items:
        product = await db.get(Product, item.product_id)
        if not product or not product.is_active:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not available")
        subtotal += product.sale_price * item.quantity
        items_detail.append({"product_id": item.product_id, "quantity": item.quantity, "price": product.sale_price})

    shipping_cost = 0.0  # Free shipping
    tax = round(subtotal * 0.0, 2)  # Set tax rate as needed
    total = subtotal + shipping_cost + tax

    stripe_service = StripeService()
    payment_data = await stripe_service.create_payment_intent(
        amount_cents=int(total * 100),
        metadata={
            "customer_email": checkout.email,
            "customer_name": checkout.name,
            "items_count": len(checkout.items),
        },
    )

    return {
        "client_secret": payment_data["client_secret"],
        "payment_intent_id": payment_data["payment_intent_id"],
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "tax": tax,
        "total": total,
        "items": items_detail,
    }


@router.post("/confirm")
async def confirm_order(payload: ConfirmOrder, db: AsyncSession = Depends(get_db)):
    """
    Step 2: After Stripe payment succeeds on frontend, confirm the order.
    This creates the order record and triggers automatic supplier fulfillment.
    """
    stripe_service = StripeService()
    payment = await stripe_service.confirm_payment(payload.payment_intent_id)

    if payment["status"] != "succeeded":
        raise HTTPException(status_code=400, detail=f"Payment not confirmed: {payment['status']}")

    order_service = OrderService(db)

    # Build order data
    from app.models.product import Product
    items_with_cost = []
    subtotal = 0.0
    for item in payload.checkout_data.items:
        product = await db.get(Product, item.product_id)
        items_with_cost.append({"product_id": item.product_id, "quantity": item.quantity})
        subtotal += product.sale_price * item.quantity

    order = await order_service.create_order({
        "email": payload.checkout_data.email,
        "name": payload.checkout_data.name,
        "phone": payload.checkout_data.phone,
        "shipping_address": payload.checkout_data.shipping_address.model_dump(),
        "payment_intent_id": payload.payment_intent_id,
        "items": items_with_cost,
        "subtotal": subtotal,
        "shipping_cost": 0.0,
        "tax": 0.0,
        "total": subtotal,
    })

    # Mark as payment confirmed, then auto-fulfill
    charge_id = payment.get("charges", [{}])[0].get("charge_id", "") if payment.get("charges") else ""
    await order_service.mark_payment_confirmed(payload.payment_intent_id, charge_id)
    await order_service.fulfill_order(order.id)

    return {
        "order_id": order.id,
        "order_number": order.order_number,
        "status": "confirmed",
        "message": "Order confirmed! You'll receive a tracking number once shipped.",
    }


@router.get("/{order_number}/tracking")
async def get_order_tracking(order_number: str, email: str, db: AsyncSession = Depends(get_db)):
    """Customer order tracking lookup (requires email verification)."""
    from app.models.order import Order
    result = await db.execute(
        select(Order).where(
            Order.order_number == order_number,
            Order.customer_email == email,
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_number": order.order_number,
        "status": order.status,
        "tracking_number": order.tracking_number,
        "tracking_url": order.tracking_url,
        "carrier": order.carrier,
        "estimated_delivery": order.estimated_delivery_days if hasattr(order, "estimated_delivery_days") else None,
    }
