"""
Admin API — protected endpoints for monitoring and management.
JWT-protected. Exposes AI analytics, security scans, and store controls.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone, date
from app.database import get_db
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.analytics import DailyReport, AnalyticsEvent
from app.models.security import SecurityScan
from app.config import get_settings
import structlog

log = structlog.get_logger()
router = APIRouter()
security = HTTPBearer()
settings = get_settings()


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=8)) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/auth/login")
async def admin_login(credentials: dict):
    """Admin login — returns JWT token."""
    if (
        credentials.get("email") != settings.admin_email
        or credentials.get("password") != settings.admin_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": settings.admin_email, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """Main admin dashboard — real-time store metrics."""
    today = date.today().isoformat()

    # Today's orders
    orders_result = await db.execute(
        select(Order).where(func.date(Order.created_at) == today)
    )
    today_orders = orders_result.scalars().all()

    today_revenue = sum(o.total for o in today_orders if o.payment_status == "paid")
    today_profit = sum(o.profit for o in today_orders if o.payment_status == "paid")

    # All-time
    all_revenue = await db.execute(
        select(func.sum(Order.total)).where(Order.payment_status == "paid")
    )
    all_profit = await db.execute(
        select(func.sum(Order.profit)).where(Order.payment_status == "paid")
    )
    total_orders = await db.execute(select(func.count(Order.id)))
    active_products = await db.execute(
        select(func.count(Product.id)).where(Product.is_active == True)
    )

    # Recent orders
    recent = await db.execute(
        select(Order).order_by(desc(Order.created_at)).limit(10)
    )

    # Latest AI report
    latest_report = await db.execute(
        select(DailyReport).order_by(desc(DailyReport.report_date)).limit(1)
    )
    report = latest_report.scalar_one_or_none()

    # Latest security scan
    latest_scan = await db.execute(
        select(SecurityScan).order_by(desc(SecurityScan.created_at)).limit(1)
    )
    scan = latest_scan.scalar_one_or_none()

    return {
        "today": {
            "revenue": today_revenue,
            "profit": today_profit,
            "orders": len(today_orders),
            "profit_margin": (today_profit / today_revenue * 100) if today_revenue else 0,
        },
        "all_time": {
            "revenue": all_revenue.scalar() or 0,
            "profit": all_profit.scalar() or 0,
            "orders": total_orders.scalar() or 0,
            "active_products": active_products.scalar() or 0,
        },
        "recent_orders": [
            {
                "order_number": o.order_number,
                "customer": o.customer_name,
                "total": o.total,
                "status": o.status,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in recent.scalars().all()
        ],
        "latest_ai_report": {
            "date": report.report_date if report else None,
            "executive_summary": report.ai_insights if report else "No report yet",
            "recommendations": report.ai_recommendations if report else [],
            "performance_score": None,
        } if report else None,
        "security_status": {
            "last_scan": scan.created_at.isoformat() if scan and scan.created_at else None,
            "risk_level": scan.risk_level if scan else "unknown",
            "findings_count": len(scan.findings) if scan else 0,
        } if scan else None,
    }


@router.get("/orders")
async def list_orders(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
    status_filter: str = None,
    limit: int = 50,
):
    """List orders with optional status filter."""
    query = select(Order).order_by(desc(Order.created_at)).limit(limit)
    if status_filter:
        query = query.where(Order.status == status_filter)
    result = await db.execute(query)
    orders = result.scalars().all()
    return [
        {
            "id": o.id,
            "order_number": o.order_number,
            "customer_email": o.customer_email,
            "customer_name": o.customer_name,
            "total": o.total,
            "profit": o.profit,
            "status": o.status,
            "tracking_number": o.tracking_number,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]


@router.get("/products")
async def list_products_admin(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """List all products with performance data."""
    result = await db.execute(select(Product).order_by(desc(Product.sale_count)))
    products = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "sale_price": p.sale_price,
            "cost_price": p.cost_price,
            "profit_per_unit": p.sale_price - p.cost_price,
            "margin_percent": ((p.sale_price - p.cost_price) / p.sale_price * 100),
            "sale_count": p.sale_count,
            "view_count": p.view_count,
            "is_active": p.is_active,
            "is_featured": p.is_featured,
            "is_trending": p.is_trending,
            "ai_trend_score": p.ai_trend_score,
        }
        for p in products
    ]


@router.patch("/products/{product_id}")
async def update_product(
    product_id: str,
    updates: dict,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """Update product fields (price, active status, featured, etc.)."""
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    allowed_fields = {"sale_price", "compare_at_price", "is_active", "is_featured", "is_trending"}
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(product, field, value)

    await db.commit()
    return {"status": "updated", "product_id": product_id}


@router.get("/analytics/reports")
async def get_analytics_reports(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
    limit: int = 30,
):
    """Get historical daily reports."""
    result = await db.execute(
        select(DailyReport).order_by(desc(DailyReport.report_date)).limit(limit)
    )
    reports = result.scalars().all()
    return [
        {
            "date": r.report_date,
            "revenue": r.total_revenue,
            "profit": r.total_profit,
            "orders": r.orders_count,
            "margin": r.profit_margin,
            "insights": r.ai_insights,
        }
        for r in reports
    ]


@router.get("/security/scans")
async def get_security_scans(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_admin),
):
    """Get recent security scan results."""
    result = await db.execute(
        select(SecurityScan).order_by(desc(SecurityScan.created_at)).limit(10)
    )
    scans = result.scalars().all()
    return [
        {
            "id": s.id,
            "scan_type": s.scan_type,
            "risk_level": s.risk_level,
            "findings_count": len(s.findings),
            "recommendations": s.recommendations,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in scans
    ]


@router.post("/automation/trigger/{task}")
async def trigger_automation(
    task: str,
    _: dict = Depends(get_current_admin),
):
    """Manually trigger an automation task (normally runs on schedule)."""
    from app.automation.scheduler import run_task_by_name
    valid_tasks = ["product_discovery", "price_update", "inventory_sync", "security_scan", "daily_report"]
    if task not in valid_tasks:
        raise HTTPException(status_code=400, detail=f"Unknown task. Valid: {valid_tasks}")

    # Fire and forget
    import asyncio
    asyncio.create_task(run_task_by_name(task))
    return {"status": "triggered", "task": task}
