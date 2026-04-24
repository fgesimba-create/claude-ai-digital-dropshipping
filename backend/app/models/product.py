from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    short_description: Mapped[str] = mapped_column(String(500), nullable=True)

    # Pricing
    cost_price: Mapped[float] = mapped_column(Float, nullable=False)   # supplier cost
    sale_price: Mapped[float] = mapped_column(Float, nullable=False)   # what we charge
    compare_at_price: Mapped[float] = mapped_column(Float, nullable=True)  # "was" price

    # Inventory
    stock_quantity: Mapped[int] = mapped_column(Integer, default=999)
    track_inventory: Mapped[bool] = mapped_column(Boolean, default=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_trending: Mapped[bool] = mapped_column(Boolean, default=False)

    # Supplier linkage
    supplier_id: Mapped[str] = mapped_column(String(36), ForeignKey("suppliers.id"), nullable=True)
    supplier_product_id: Mapped[str] = mapped_column(String(255), nullable=True)
    supplier_sku: Mapped[str] = mapped_column(String(255), nullable=True)

    # Category
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("product_categories.id"), nullable=True)

    # SEO / AI-generated metadata
    meta_title: Mapped[str] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str] = mapped_column(String(500), nullable=True)
    tags: Mapped[dict] = mapped_column(JSON, default=list)

    # Analytics
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    sale_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)

    # Shipping
    weight_grams: Mapped[int] = mapped_column(Integer, nullable=True)
    ships_from: Mapped[str] = mapped_column(String(100), nullable=True)
    estimated_delivery_days: Mapped[str] = mapped_column(String(50), nullable=True)

    # AI scoring
    ai_trend_score: Mapped[float] = mapped_column(Float, default=0.0)
    ai_profit_score: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    category: Mapped["ProductCategory"] = relationship("ProductCategory", back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    alt_text: Mapped[str] = mapped_column(String(255), nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped["Product"] = relationship("Product", back_populates="images")
