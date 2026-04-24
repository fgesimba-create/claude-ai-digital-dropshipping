"""Email and Slack notifications for orders, alerts, and reports."""
import httpx
import structlog
from app.config import get_settings

log = structlog.get_logger()
settings = get_settings()


class NotificationService:
    async def send_order_confirmation(self, order) -> None:
        """Send order confirmation email to customer."""
        if not settings.sendgrid_api_key:
            log.info("notification.skip_no_sendgrid", order=order.order_number)
            return

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={"Authorization": f"Bearer {settings.sendgrid_api_key}"},
                    json={
                        "personalizations": [
                            {
                                "to": [{"email": order.customer_email, "name": order.customer_name}],
                                "dynamic_template_data": {
                                    "order_number": order.order_number,
                                    "customer_name": order.customer_name,
                                    "total": f"${order.total:.2f}",
                                    "store_name": settings.store_name,
                                },
                            }
                        ],
                        "from": {"email": settings.store_email, "name": settings.store_name},
                        "subject": f"Order Confirmed #{order.order_number} — {settings.store_name}",
                        "content": [
                            {
                                "type": "text/html",
                                "value": f"""
<h2>Thanks for your order, {order.customer_name}!</h2>
<p>Your order <strong>#{order.order_number}</strong> has been confirmed and will be shipped soon.</p>
<p><strong>Total: ${order.total:.2f}</strong></p>
<p>You'll receive tracking info as soon as your order ships.</p>
<br>
<p>— The {settings.store_name} Team</p>
""",
                            }
                        ],
                    },
                )
        except Exception as e:
            log.error("notification.order_email_failed", order=order.order_number, error=str(e))

    async def send_shipping_update(self, order) -> None:
        """Notify customer that their order has shipped with tracking info."""
        if not settings.sendgrid_api_key:
            return

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={"Authorization": f"Bearer {settings.sendgrid_api_key}"},
                    json={
                        "personalizations": [
                            {
                                "to": [{"email": order.customer_email, "name": order.customer_name}],
                            }
                        ],
                        "from": {"email": settings.store_email, "name": settings.store_name},
                        "subject": f"Your Order #{order.order_number} Has Shipped!",
                        "content": [
                            {
                                "type": "text/html",
                                "value": f"""
<h2>Your order is on its way! 📦</h2>
<p>Order <strong>#{order.order_number}</strong> has shipped via {order.carrier or "our carrier"}.</p>
<p><strong>Tracking Number:</strong> {order.tracking_number or "Not yet available"}</p>
{f'<p><a href="{order.tracking_url}">Track Your Package</a></p>' if order.tracking_url else ""}
<br>
<p>— The {settings.store_name} Team</p>
""",
                            }
                        ],
                    },
                )
        except Exception as e:
            log.error("notification.shipping_email_failed", order=order.order_number, error=str(e))

    async def alert_admin(self, message: str) -> None:
        """Send an alert to the admin via Slack webhook."""
        if not settings.slack_webhook_url:
            log.warning("notification.admin_alert", message=message)
            return

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    settings.slack_webhook_url,
                    json={"text": f"🚨 *{settings.store_name} Alert*\n{message}"},
                )
        except Exception as e:
            log.error("notification.slack_failed", error=str(e))

    async def send_daily_report(self, report: dict) -> None:
        """Send the AI-generated daily analytics report to admin."""
        if not settings.slack_webhook_url:
            return

        summary = report.get("executive_summary", "No summary available")
        score = report.get("performance_score", 0)
        revenue = report.get("revenue_analysis", {}).get("assessment", "")

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    settings.slack_webhook_url,
                    json={
                        "text": f"📊 *Daily Report — {settings.store_name}*\n"
                                f"Score: {score}/10\n"
                                f"{summary}\n"
                                f"_{revenue}_"
                    },
                )
        except Exception as e:
            log.error("notification.daily_report_failed", error=str(e))
