"""Product catalog API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.database import get_db
from app.models.product import Product, ProductCategory, ProductImage
from pydantic import BaseModel
from typing import Optional
import structlog

log = structlog.get_logger()
router = APIRouter()


class ProductResponse(BaseModel):
    id: str
    name: str
    slug: str
    short_description: Optional[str]
    description: Optional[str]
    sale_price: float
    compare_at_price: Optional[float]
    is_featured: bool
    is_trending: bool
    rating: float
    review_count: int
    sale_count: int
    ships_from: Optional[str]
    estimated_delivery_days: Optional[str]
    category: Optional[dict]
    images: list[dict]
    tags: list
    key_features: Optional[list]

    class Config:
        from_attributes = True


def product_to_dict(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "slug": p.slug,
        "short_description": p.short_description,
        "description": p.description,
        "sale_price": p.sale_price,
        "compare_at_price": p.compare_at_price,
        "is_featured": p.is_featured,
        "is_trending": p.is_trending,
        "rating": p.rating,
        "review_count": p.review_count,
        "sale_count": p.sale_count,
        "ships_from": p.ships_from,
        "estimated_delivery_days": p.estimated_delivery_days,
        "category": {
            "id": p.category.id,
            "name": p.category.name,
            "slug": p.category.slug,
        } if p.category else None,
        "images": [
            {"url": img.url, "alt_text": img.alt_text, "is_primary": img.is_primary}
            for img in sorted(p.images, key=lambda x: x.position)
        ],
        "tags": p.tags or [],
    }


@router.get("")
async def list_products(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = Query("featured", enum=["featured", "price_asc", "price_desc", "newest", "trending"]),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    """Get paginated product listing with filtering and sorting."""
    query = select(Product).where(Product.is_active == True)

    if category:
        query = query.join(ProductCategory).where(ProductCategory.slug == category)
    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.short_description.ilike(f"%{search}%"),
            )
        )
    if min_price is not None:
        query = query.where(Product.sale_price >= min_price)
    if max_price is not None:
        query = query.where(Product.sale_price <= max_price)

    sort_map = {
        "featured": Product.is_featured.desc(),
        "price_asc": Product.sale_price.asc(),
        "price_desc": Product.sale_price.desc(),
        "newest": Product.created_at.desc(),
        "trending": Product.ai_trend_score.desc(),
    }
    query = query.order_by(sort_map[sort])

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()

    # Batch load relationships
    for p in products:
        await db.refresh(p, ["images", "category"])

    return {
        "products": [product_to_dict(p) for p in products],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/featured")
async def get_featured_products(db: AsyncSession = Depends(get_db), limit: int = 8):
    """Get featured products for homepage."""
    result = await db.execute(
        select(Product)
        .where(Product.is_active == True, Product.is_featured == True)
        .order_by(Product.ai_trend_score.desc())
        .limit(limit)
    )
    products = result.scalars().all()
    for p in products:
        await db.refresh(p, ["images", "category"])
    return [product_to_dict(p) for p in products]


@router.get("/trending")
async def get_trending_products(db: AsyncSession = Depends(get_db), limit: int = 8):
    """Get currently trending products."""
    result = await db.execute(
        select(Product)
        .where(Product.is_active == True, Product.is_trending == True)
        .order_by(Product.sale_count.desc(), Product.ai_trend_score.desc())
        .limit(limit)
    )
    products = result.scalars().all()
    for p in products:
        await db.refresh(p, ["images", "category"])
    return [product_to_dict(p) for p in products]


@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get all product categories."""
    result = await db.execute(select(ProductCategory).order_by(ProductCategory.name))
    categories = result.scalars().all()
    return [
        {"id": c.id, "name": c.name, "slug": c.slug, "icon": c.icon}
        for c in categories
    ]


@router.get("/{slug}")
async def get_product(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a single product by slug."""
    result = await db.execute(
        select(Product).where(Product.slug == slug, Product.is_active == True)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.refresh(product, ["images", "category"])

    # Track view
    product.view_count += 1
    await db.commit()

    return product_to_dict(product)
