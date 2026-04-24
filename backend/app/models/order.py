from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class OrderStatus(str, enum.Enum):
    pending = "pending"
    payment_confirmed = "payment_confirmed"
    submitted_to_supplier = "submitted_to_supplier"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Customer info
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(50), nullable=True)

    # Shipping address
    shipping_address: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Payment
    stripe_payment_intent_id: Mapped[str] = mapped_column(String(255), nullable=True)
    stripe_charge_id: Mapped[str] = mapped_column(String(255), nullable=True)
    payment_status: Mapped[str] = mapped_column(String(50), default="pending")

    # Order status
    status: Mapped[str] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.pending
    )

    # Financials
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    shipping_cost: Mapped[float] = mapped_column(Float, default=0.0)
    tax: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    supplier_cost: Mapped[float] = mapped_column(Float, default=0.0)
    profit: Mapped[float] = mapped_column(Float, default=0.0)

    # Supplier fulfillment
    supplier_order_id: Mapped[str] = mapped_column(String(255), nullable=True)
    tracking_number: Mapped[str] = mapped_column(String(255), nullable=True)
    tracking_url: Mapped[str] = mapped_column(String(500), nullable=True)
    carrier: Mapped[str] = mapped_column(String(100), nullable=True)

    # Notes
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    fulfillment_log: Mapped[list] = mapped_column(JSON, default=list)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    fulfilled_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)

    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_sku: Mapped[str] = mapped_column(String(255), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
