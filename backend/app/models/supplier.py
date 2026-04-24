from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_name: Mapped[str] = mapped_column(String(100), nullable=False)  # "cjdropshipping", etc.
    website: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Performance metrics (updated by AI analytics agent)
    avg_processing_days: Mapped[float] = mapped_column(Float, default=2.0)
    avg_shipping_days: Mapped[float] = mapped_column(Float, default=8.0)
    fulfillment_rate: Mapped[float] = mapped_column(Float, default=0.98)
    defect_rate: Mapped[float] = mapped_column(Float, default=0.02)
    reliability_score: Mapped[float] = mapped_column(Float, default=0.95)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    products: Mapped[list["Product"]] = relationship("Product", back_populates="supplier")
    supplier_products: Mapped[list["SupplierProduct"]] = relationship("SupplierProduct", back_populates="supplier")


class SupplierProduct(Base):
    """Maps our internal products to supplier catalog entries."""
    __tablename__ = "supplier_products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    supplier_id: Mapped[str] = mapped_column(String(36), nullable=False)
    supplier_product_id: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier_sku: Mapped[str] = mapped_column(String(255), nullable=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    stock_available: Mapped[int] = mapped_column(Integer, default=0)
    images: Mapped[list] = mapped_column(JSON, default=list)
    variants: Mapped[list] = mapped_column(JSON, default=list)
    raw_data: Mapped[dict] = mapped_column(JSON, default=dict)

    last_synced_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="supplier_products")
