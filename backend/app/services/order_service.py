"""
Order orchestration service — bridges customer orders to supplier fulfillment.
Fully automated: payment confirmed → supplier order placed → tracking synced.
"""
import random
import string
import structlog
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.services.cjdropshipping import CJDropshippingService
from app.services.notification_service import NotificationService

log = structlog.get_logger()


def generate_order_number() -> str:
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=8))
    return f"TF-{suffix}"


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cj = CJDropshippingService()
        self.notify = NotificationService()

    async def create_order(self, order_data: dict) -> Order:
        """Create an order record from a validated checkout submission."""
        order = Order(
            order_number=generate_order_number(),
            customer_email=order_data["email"],
            customer_name=order_data["name"],
            customer_phone=order_data.get("phone"),
            shipping_address=order_data["shipping_address"],
            stripe_payment_intent_id=order_data["payment_intent_id"],
            subtotal=order_data["subtotal"],
            shipping_cost=order_data.get("shipping_cost", 0),
            tax=order_data.get("tax", 0),
            total=order_data["total"],
            status=OrderStatus.pending,
        )
        self.db.add(order)
        await self.db.flush()

        supplier_cost_total = 0.0
        for item_data in order_data["items"]:
            product = await self.db.get(Product, item_data["product_id"])
            if not product:
                continue

            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_sku=product.supplier_sku,
                quantity=item_data["quantity"],
                unit_price=product.sale_price,
                unit_cost=product.cost_price,
                total_price=product.sale_price * item_data["quantity"],
            )
            self.db.add(item)
            supplier_cost_total += product.cost_price * item_data["quantity"]

            # Update sale count
            product.sale_count += item_data["quantity"]

        order.supplier_cost = supplier_cost_total
        order.profit = order.total - supplier_cost_total
        await self.db.commit()
        await self.db.refresh(order)

        log.info("order.created", order_id=order.id, order_number=order.order_number)
        return order

    async def fulfill_order(self, order_id: str) -> Order:
        """
        After payment confirmation, automatically submit order to CJDropshipping.
        This is the core automation — no human touches required.
        """
        order = await self.db.get(Order, order_id, options=[])
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.status != OrderStatus.payment_confirmed:
            log.warning("order.fulfill_skipped", order_id=order_id, status=order.status)
            return order

        # Load items
        items_result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        items = items_result.scalars().all()

        fulfillment_payload = {
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "shipping_address": order.shipping_address,
            "items": [
                {
                    "supplier_sku": item.product_sku,
                    "quantity": item.quantity,
                }
                for item in items
            ],
        }

        try:
            await self.cj.authenticate()
            cj_result = await self.cj.create_order(fulfillment_payload)

            order.supplier_order_id = cj_result.get("orderId")
            order.status = OrderStatus.submitted_to_supplier
            order.fulfillment_log = order.fulfillment_log + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": "submitted_to_cj",
                    "cj_order_id": cj_result.get("orderId"),
                }
            ]
            await self.db.commit()

            await self.notify.send_order_confirmation(order)
            log.info("order.fulfilled", order_id=order_id, cj_order_id=cj_result.get("orderId"))

        except Exception as e:
            log.error("order.fulfillment_failed", order_id=order_id, error=str(e))
            order.fulfillment_log = order.fulfillment_log + [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": "fulfillment_error",
                    "error": str(e),
                }
            ]
            await self.db.commit()
            await self.notify.alert_admin(f"Order fulfillment failed: {order.order_number} — {e}")
            raise

        return order

    async def sync_tracking(self, order_id: str) -> Order:
        """Sync tracking information from CJDropshipping for a fulfilled order."""
        order = await self.db.get(Order, order_id)
        if not order or not order.supplier_order_id:
            return order

        try:
            await self.cj.authenticate()
            tracking = await self.cj.get_order_tracking(order.supplier_order_id)

            if tracking and tracking.get("tracking_number"):
                order.tracking_number = tracking["tracking_number"]
                order.tracking_url = tracking.get("tracking_url")
                order.carrier = tracking.get("carrier")
                order.status = OrderStatus.shipped
                await self.db.commit()
                await self.notify.send_shipping_update(order)
                log.info("order.tracking_synced", order_id=order_id, tracking=tracking["tracking_number"])

        except Exception as e:
            log.error("order.tracking_sync_error", order_id=order_id, error=str(e))

        return order

    async def mark_payment_confirmed(self, payment_intent_id: str, charge_id: str) -> Order | None:
        """Mark order as payment confirmed after Stripe webhook fires."""
        result = await self.db.execute(
            select(Order).where(Order.stripe_payment_intent_id == payment_intent_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            return None

        order.status = OrderStatus.payment_confirmed
        order.stripe_charge_id = charge_id
        order.payment_status = "paid"
        await self.db.commit()
        return order
