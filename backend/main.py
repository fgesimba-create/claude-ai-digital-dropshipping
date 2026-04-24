"""
TechFlow AI Dropshipping Platform — Backend API
FastAPI application with automated AI agents and supplier integration.
"""
import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.database import init_db
from app.api import router
from app.automation.scheduler import scheduler, setup_scheduler
from app.config import get_settings

settings = get_settings()
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database, seed default data, start automation scheduler."""
    log.info("startup.beginning", store=settings.store_name)

    # Initialize database tables
    await init_db()
    log.info("startup.database_ready")

    # Seed default categories if empty
    await seed_default_data()

    # Start the automation scheduler
    setup_scheduler()
    scheduler.start()
    log.info("startup.scheduler_started", jobs=len(scheduler.get_jobs()))

    # Trigger initial product discovery if store is empty
    await maybe_trigger_initial_discovery()

    log.info("startup.complete", store=settings.store_name)
    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    log.info("shutdown.complete")


async def seed_default_data():
    """Seed the database with default categories and supplier on first run."""
    from app.database import AsyncSessionLocal
    from app.models.product import ProductCategory
    from app.models.supplier import Supplier
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        result = await db.execute(select(ProductCategory).limit(1))
        if result.scalar_one_or_none():
            return

        categories = [
            ProductCategory(name="Wireless Audio", slug="wireless-audio", icon="headphones"),
            ProductCategory(name="Mobile Accessories", slug="mobile-accessories", icon="smartphone"),
            ProductCategory(name="Smart Home", slug="smart-home", icon="home"),
            ProductCategory(name="Gaming", slug="gaming", icon="gamepad"),
            ProductCategory(name="Wearables", slug="wearables", icon="watch"),
            ProductCategory(name="Laptop & Desk", slug="laptop-desk", icon="laptop"),
            ProductCategory(name="LED & Lighting", slug="led-lighting", icon="lightbulb"),
            ProductCategory(name="Cameras & Drones", slug="cameras-drones", icon="camera"),
        ]

        supplier = Supplier(
            name="CJDropshipping",
            api_name="cjdropshipping",
            website="https://cjdropshipping.com",
            avg_processing_days=1.5,
            avg_shipping_days=7.0,
            fulfillment_rate=0.98,
            reliability_score=0.96,
        )

        for cat in categories:
            db.add(cat)
        db.add(supplier)
        await db.commit()
        log.info("startup.seed_complete", categories=len(categories))


async def maybe_trigger_initial_discovery():
    """If store has no products, run product discovery immediately on startup."""
    from app.database import AsyncSessionLocal
    from app.models.product import Product
    from sqlalchemy import select, func

    async with AsyncSessionLocal() as db:
        count_result = await db.execute(select(func.count(Product.id)))
        count = count_result.scalar()

    if count == 0:
        log.info("startup.no_products_triggering_discovery")
        from app.automation.scheduler import task_product_discovery
        import asyncio
        asyncio.create_task(task_product_discovery())


app = FastAPI(
    title=f"{settings.store_name} API",
    description="AI-powered dropshipping platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.store_domain, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[settings.store_domain.replace("https://", "").replace("http://", ""), "localhost"],
    )

# Mount all API routes
app.include_router(router, prefix="/api")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "store": settings.store_name,
        "automation": {
            "scheduler_running": scheduler.running,
            "jobs": [j.id for j in scheduler.get_jobs()],
        },
    }
