from sqlalchemy import String, Float, Integer, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import uuid


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # page_view, add_to_cart, purchase
    product_id: Mapped[str] = mapped_column(String(36), nullable=True)
    order_id: Mapped[str] = mapped_column(String(36), nullable=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_date: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)  # YYYY-MM-DD

    # Revenue metrics
    total_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    total_profit: Mapped[float] = mapped_column(Float, default=0.0)
    profit_margin: Mapped[float] = mapped_column(Float, default=0.0)

    # Order metrics
    orders_count: Mapped[int] = mapped_column(Integer, default=0)
    items_sold: Mapped[int] = mapped_column(Integer, default=0)
    avg_order_value: Mapped[float] = mapped_column(Float, default=0.0)

    # Traffic metrics
    page_views: Mapped[int] = mapped_column(Integer, default=0)
    unique_visitors: Mapped[int] = mapped_column(Integer, default=0)
    conversion_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # AI analysis
    ai_insights: Mapped[str] = mapped_column(Text, nullable=True)
    ai_recommendations: Mapped[list] = mapped_column(JSON, default=list)
    top_products: Mapped[list] = mapped_column(JSON, default=list)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
