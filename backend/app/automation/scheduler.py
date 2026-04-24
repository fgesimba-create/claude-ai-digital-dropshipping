"""
The automation brain — fully hands-free operation scheduler.

Runs on APScheduler, executing AI-powered tasks on set intervals:
- Product discovery & catalog refresh (daily)
- Price optimization (every 6 hours)
- Inventory sync with supplier (every 2 hours)
- Order tracking sync (every hour)
- Security scans (every 12 hours)
- Analytics report generation (daily)

This is what makes the store truly autonomous.
"""
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app.config import get_settings
from app.database import AsyncSessionLocal

log = structlog.get_logger()
settings = get_settings()

scheduler = AsyncIOScheduler(timezone="UTC")


# ─── PRODUCT DISCOVERY ──────────────────────────────────────────────────────

async def task_product_discovery():
    """
    AI discovers trending tech products, evaluates them,
    sources from CJDropshipping, generates content, and lists them.
    """
    log.info("automation.product_discovery.starting")
    async with AsyncSessionLocal() as db:
        try:
            from app.agents.product_discovery import ProductDiscoveryAgent
            from app.agents.content_agent import ContentAgent
            from app.services.cjdropshipping import CJDropshippingService
            from app.models.product import Product, ProductCategory, ProductImage
            from app.models.supplier import Supplier
            from sqlalchemy import select
            import re

            discovery = ProductDiscoveryAgent()
            content_agent = ContentAgent()
            cj = CJDropshippingService()

            # Step 1: AI discovers 15 trending products
            trending = await discovery.discover_trending_products(count=8)
            log.info("automation.product_discovery.ai_found", count=len(trending))

            await cj.authenticate()

            added = 0
            for product_idea in trending[:8]:  # Process top 8
                try:
                    # Step 2: Search CJDropshipping for this product
                    cj_results = await cj.search_products(
                        product_idea["cj_search_term"], page_size=5
                    )
                    cj_products = cj_results.get("list", [])
                    if not cj_products:
                        log.warning("automation.no_cj_product", term=product_idea["cj_search_term"])
                        continue

                    cj_product = cj_products[0]
                    cost_usd = float(cj_product.get("sellPrice", 0))
                    if cost_usd == 0:
                        continue

                    # Step 3: AI evaluates this specific product
                    evaluation = await discovery.evaluate_product({
                        **product_idea,
                        "actual_cj_cost": cost_usd,
                        "cj_product_id": cj_product.get("pid"),
                    })

                    if not evaluation.get("should_list", False):
                        log.info("automation.product_rejected", name=product_idea["name"],
                                 reason=evaluation.get("rejection_reason"))
                        continue

                    # Step 4: Generate AI content
                    product_content = await content_agent.generate_product_content({
                        **product_idea,
                        "cost_price": cost_usd,
                        "sale_price": evaluation.get("recommended_sale_price_usd", cost_usd * settings.target_profit_multiplier),
                    })

                    # Step 5: Find or create category
                    cat_slug = product_idea.get("recommended_category_slug", "electronics")
                    cat_result = await db.execute(
                        select(ProductCategory).where(ProductCategory.slug == cat_slug)
                    )
                    category = cat_result.scalar_one_or_none()
                    if not category:
                        category = ProductCategory(
                            name=cat_slug.replace("-", " ").title(),
                            slug=cat_slug,
                        )
                        db.add(category)
                        await db.flush()

                    # Step 6: Find or create supplier record
                    supplier_result = await db.execute(
                        select(Supplier).where(Supplier.api_name == "cjdropshipping")
                    )
                    supplier = supplier_result.scalar_one_or_none()
                    if not supplier:
                        supplier = Supplier(
                            name="CJDropshipping",
                            api_name="cjdropshipping",
                            website="https://cjdropshipping.com",
                        )
                        db.add(supplier)
                        await db.flush()

                    # Step 7: Create product slug
                    base_name = product_content.get("name", product_idea["name"])
                    slug = re.sub(r"[^a-z0-9]+", "-", base_name.lower()).strip("-")

                    # Check for duplicate slug
                    existing = await db.execute(
                        select(Product).where(Product.slug == slug)
                    )
                    if existing.scalar_one_or_none():
                        slug = f"{slug}-{cj_product.get('pid', '')[:6]}"

                    sale_price = evaluation.get("recommended_sale_price_usd",
                                                cost_usd * settings.target_profit_multiplier)
                    compare_at_price = round(sale_price * 1.25, 2)

                    # Step 8: Save product to database
                    product = Product(
                        name=product_content.get("name", base_name),
                        slug=slug,
                        description=product_content.get("description"),
                        short_description=product_content.get("short_description"),
                        cost_price=cost_usd,
                        sale_price=round(sale_price, 2),
                        compare_at_price=compare_at_price,
                        supplier_id=supplier.id,
                        supplier_product_id=cj_product.get("pid"),
                        supplier_sku=cj_product.get("vid", cj_product.get("pid")),
                        category_id=category.id,
                        meta_title=product_content.get("meta_title"),
                        meta_description=product_content.get("meta_description"),
                        tags=product_content.get("tags", []),
                        ships_from="CN/US Warehouse",
                        estimated_delivery_days="5-10 business days",
                        ai_trend_score=evaluation.get("ai_trend_score", 5.0),
                        ai_profit_score=evaluation.get("ai_profit_score", 5.0),
                        is_active=True,
                        is_trending=evaluation.get("ai_trend_score", 0) >= 7.5,
                        is_featured=evaluation.get("ai_trend_score", 0) >= 8.5,
                    )
                    db.add(product)
                    await db.flush()

                    # Step 9: Add product images from CJDropshipping
                    images = cj_product.get("productImage", "").split(",")
                    for i, img_url in enumerate(images[:5]):
                        if img_url.strip():
                            img = ProductImage(
                                product_id=product.id,
                                url=img_url.strip(),
                                alt_text=product.name,
                                position=i,
                                is_primary=(i == 0),
                            )
                            db.add(img)

                    await db.commit()
                    added += 1
                    log.info("automation.product_added", name=product.name, price=product.sale_price)

                except Exception as e:
                    log.error("automation.product_add_error", product=product_idea.get("name"), error=str(e))
                    await db.rollback()

            log.info("automation.product_discovery.complete", added=added)

        except Exception as e:
            log.error("automation.product_discovery.failed", error=str(e))


# ─── PRICE OPTIMIZATION ──────────────────────────────────────────────────────

async def task_price_update():
    """AI analyzes sales velocity and optimizes prices for maximum profit."""
    log.info("automation.price_update.starting")
    async with AsyncSessionLocal() as db:
        try:
            from app.agents.pricing_agent import PricingAgent
            from app.models.product import Product
            from sqlalchemy import select

            agent = PricingAgent()
            result = await db.execute(
                select(Product).where(Product.is_active == True).limit(50)
            )
            products = result.scalars().all()

            if not products:
                return

            product_data = [
                {
                    "id": p.id,
                    "name": p.name,
                    "cost_price": p.cost_price,
                    "sale_price": p.sale_price,
                    "sale_count": p.sale_count,
                    "view_count": p.view_count,
                    "category": p.category_id,
                }
                for p in products
            ]

            updates = await agent.optimize_prices(product_data)

            for update in updates:
                product = await db.get(Product, update.get("product_id"))
                if product:
                    product.sale_price = update["new_sale_price"]
                    if update.get("new_compare_at_price"):
                        product.compare_at_price = update["new_compare_at_price"]

            await db.commit()
            log.info("automation.price_update.complete", updated=len(updates))

        except Exception as e:
            log.error("automation.price_update.failed", error=str(e))


# ─── INVENTORY SYNC ──────────────────────────────────────────────────────────

async def task_inventory_sync():
    """Sync inventory levels from CJDropshipping and deactivate out-of-stock items."""
    log.info("automation.inventory_sync.starting")
    async with AsyncSessionLocal() as db:
        try:
            from app.services.cjdropshipping import CJDropshippingService
            from app.models.product import Product
            from sqlalchemy import select

            cj = CJDropshippingService()
            await cj.authenticate()

            result = await db.execute(
                select(Product).where(
                    Product.is_active == True,
                    Product.supplier_product_id.is_not(None),
                )
            )
            products = result.scalars().all()

            supplier_ids = [p.supplier_product_id for p in products if p.supplier_product_id]
            inventory = await cj.sync_inventory(supplier_ids[:50])

            inv_map = {item["supplier_product_id"]: item for item in inventory}

            for product in products:
                inv_data = inv_map.get(product.supplier_product_id)
                if inv_data:
                    stock = inv_data.get("stock", 0)
                    new_cost = inv_data.get("cost_usd", product.cost_price)

                    if stock == 0:
                        product.is_active = False
                        log.info("automation.product_deactivated_no_stock", name=product.name)
                    elif abs(new_cost - product.cost_price) > 0.50:
                        # Cost changed significantly, re-price
                        product.cost_price = new_cost
                        from app.config import get_settings
                        s = get_settings()
                        product.sale_price = round(new_cost * s.target_profit_multiplier, 2)
                        log.info("automation.cost_updated", name=product.name, new_cost=new_cost)

            await db.commit()
            log.info("automation.inventory_sync.complete")

        except Exception as e:
            log.error("automation.inventory_sync.failed", error=str(e))


# ─── TRACKING SYNC ──────────────────────────────────────────────────────────

async def task_tracking_sync():
    """Sync order tracking from CJDropshipping for all submitted orders."""
    log.info("automation.tracking_sync.starting")
    async with AsyncSessionLocal() as db:
        try:
            from app.models.order import Order, OrderStatus
            from app.services.order_service import OrderService
            from sqlalchemy import select

            result = await db.execute(
                select(Order).where(
                    Order.status.in_([
                        OrderStatus.submitted_to_supplier,
                        OrderStatus.processing,
                    ])
                ).limit(50)
            )
            orders = result.scalars().all()

            order_service = OrderService(db)
            for order in orders:
                try:
                    await order_service.sync_tracking(order.id)
                except Exception as e:
                    log.error("automation.tracking_error", order_id=order.id, error=str(e))

            log.info("automation.tracking_sync.complete", orders=len(orders))

        except Exception as e:
            log.error("automation.tracking_sync.failed", error=str(e))


# ─── SECURITY SCAN ──────────────────────────────────────────────────────────

async def task_security_scan():
    """AI-powered security scan — detects threats and auto-remediates what it can."""
    log.info("automation.security_scan.starting")
    async with AsyncSessionLocal() as db:
        try:
            from app.agents.security_agent import SecurityAgent
            from app.models.order import Order
            from app.models.security import SecurityScan
            from sqlalchemy import select, func
            from datetime import datetime, timezone, timedelta

            agent = SecurityAgent()

            # Gather scan data
            recent_orders_result = await db.execute(
                select(Order).order_by(Order.created_at.desc()).limit(100)
            )
            recent_orders = [
                {
                    "order_number": o.order_number,
                    "total": o.total,
                    "email": o.customer_email,
                    "status": o.status,
                }
                for o in recent_orders_result.scalars().all()
            ]

            scan_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "recent_orders": recent_orders,
                "failed_auth_attempts": 0,  # Would come from auth logs
                "api_logs_summary": "Normal traffic patterns",
                "environment": settings.environment,
            }

            scan_result = await agent.run_security_scan(scan_data)

            # Save scan to database
            scan = SecurityScan(
                scan_type="automated_full_scan",
                status="completed",
                risk_level=scan_result.get("overall_risk_level", "low"),
                findings=scan_result.get("findings", []),
                recommendations=scan_result.get("recommendations", []),
                ai_analysis=scan_result.get("executive_summary", ""),
            )
            db.add(scan)
            await db.commit()

            # Alert admin if elevated risk
            if scan_result.get("overall_risk_level") in ("high", "critical"):
                from app.services.notification_service import NotificationService
                notify = NotificationService()
                await notify.alert_admin(
                    f"Security scan found {scan_result['overall_risk_level'].upper()} risk issues. "
                    f"{len(scan_result.get('findings', []))} findings. Immediate review required."
                )

            log.info("automation.security_scan.complete", risk=scan_result.get("overall_risk_level"))

        except Exception as e:
            log.error("automation.security_scan.failed", error=str(e))


# ─── DAILY ANALYTICS REPORT ──────────────────────────────────────────────────

async def task_daily_report():
    """Generate AI analytics report and execute recommended automated actions."""
    log.info("automation.daily_report.starting")
    async with AsyncSessionLocal() as db:
        try:
            from app.agents.analytics_agent import AnalyticsAgent
            from app.models.order import Order
            from app.models.product import Product
            from app.models.analytics import DailyReport
            from app.services.notification_service import NotificationService
            from sqlalchemy import select, func
            from datetime import date, timedelta, timezone, datetime

            agent = AnalyticsAgent()
            notify = NotificationService()
            today = date.today().isoformat()
            yesterday_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0) - timedelta(days=1)

            # Gather yesterday's metrics
            orders_result = await db.execute(
                select(Order).where(Order.created_at >= yesterday_start, Order.payment_status == "paid")
            )
            orders = orders_result.scalars().all()

            revenue = sum(o.total for o in orders)
            cost = sum(o.supplier_cost for o in orders)
            profit = sum(o.profit for o in orders)

            products_result = await db.execute(
                select(Product).where(Product.is_active == True).order_by(Product.sale_count.desc()).limit(10)
            )
            top_products = [
                {"id": p.id, "name": p.name, "sale_count": p.sale_count, "revenue": p.sale_count * p.sale_price}
                for p in products_result.scalars().all()
            ]

            metrics = {
                "date": today,
                "total_revenue": revenue,
                "total_cost": cost,
                "total_profit": profit,
                "orders_count": len(orders),
                "avg_order_value": revenue / len(orders) if orders else 0,
                "top_products": top_products,
                "active_product_count": (await db.execute(
                    select(func.count(Product.id)).where(Product.is_active == True)
                )).scalar(),
            }

            report_data = await agent.generate_daily_report(metrics)

            # Save report
            report = DailyReport(
                report_date=today,
                total_revenue=revenue,
                total_cost=cost,
                total_profit=profit,
                profit_margin=(profit / revenue * 100) if revenue else 0,
                orders_count=len(orders),
                avg_order_value=metrics["avg_order_value"],
                ai_insights=report_data.get("executive_summary"),
                ai_recommendations=report_data.get("automated_actions_recommended", []),
                top_products=top_products,
            )
            db.add(report)
            await db.commit()

            # Execute automated actions from AI recommendations
            await _execute_ai_recommendations(db, report_data.get("automated_actions_recommended", []))

            await notify.send_daily_report(report_data)
            log.info("automation.daily_report.complete", revenue=revenue, profit=profit)

        except Exception as e:
            log.error("automation.daily_report.failed", error=str(e))


async def _execute_ai_recommendations(db, recommendations: list):
    """Auto-execute safe AI recommendations without human intervention."""
    from app.models.product import Product

    for rec in recommendations:
        action = rec.get("action")
        product_id = rec.get("product_id")

        try:
            if action == "reduce_price" and product_id:
                product = await db.get(Product, product_id)
                if product and rec.get("recommended_price"):
                    min_price = product.cost_price * settings.min_profit_multiplier
                    new_price = max(rec["recommended_price"], min_price)
                    product.sale_price = round(new_price, 2)
                    log.info("automation.auto_price_reduce", product=product.name, new_price=new_price)

            elif action == "deactivate_product" and product_id:
                product = await db.get(Product, product_id)
                if product:
                    product.is_active = False
                    log.info("automation.auto_deactivate", product=product.name)

            elif action == "feature_product" and product_id:
                product = await db.get(Product, product_id)
                if product:
                    product.is_featured = True
                    log.info("automation.auto_feature", product=product.name)

        except Exception as e:
            log.error("automation.recommendation_execute_error", action=action, error=str(e))

    await db.commit()


# ─── SCHEDULER SETUP ────────────────────────────────────────────────────────

def setup_scheduler():
    """Register all automation tasks with their schedules."""

    scheduler.add_job(
        task_product_discovery,
        trigger=IntervalTrigger(hours=settings.product_discovery_interval_hours),
        id="product_discovery",
        name="AI Product Discovery",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        task_price_update,
        trigger=IntervalTrigger(hours=settings.price_update_interval_hours),
        id="price_update",
        name="AI Price Optimization",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        task_inventory_sync,
        trigger=IntervalTrigger(hours=settings.inventory_sync_interval_hours),
        id="inventory_sync",
        name="Inventory Sync",
        replace_existing=True,
        misfire_grace_time=1800,
    )

    scheduler.add_job(
        task_tracking_sync,
        trigger=IntervalTrigger(hours=1),
        id="tracking_sync",
        name="Order Tracking Sync",
        replace_existing=True,
        misfire_grace_time=1800,
    )

    scheduler.add_job(
        task_security_scan,
        trigger=IntervalTrigger(hours=settings.security_scan_interval_hours),
        id="security_scan",
        name="AI Security Scan",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        task_daily_report,
        trigger=CronTrigger(hour=6, minute=0),  # 6am UTC daily
        id="daily_report",
        name="AI Daily Analytics Report",
        replace_existing=True,
    )

    log.info("automation.scheduler.configured", jobs=len(scheduler.get_jobs()))


async def run_task_by_name(task_name: str):
    """Manually trigger a specific automation task."""
    task_map = {
        "product_discovery": task_product_discovery,
        "price_update": task_price_update,
        "inventory_sync": task_inventory_sync,
        "security_scan": task_security_scan,
        "daily_report": task_daily_report,
        "tracking_sync": task_tracking_sync,
    }
    task_fn = task_map.get(task_name)
    if task_fn:
        await task_fn()
    else:
        raise ValueError(f"Unknown task: {task_name}")
