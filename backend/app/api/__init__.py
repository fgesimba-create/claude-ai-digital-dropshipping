from fastapi import APIRouter
from app.api import products, orders, admin, webhooks

router = APIRouter()
router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(orders.router, prefix="/orders", tags=["orders"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
