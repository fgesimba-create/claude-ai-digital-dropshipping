from sqlalchemy import String, Float, Integer, DateTime, JSON, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
import uuid


class SecurityScan(Base):
    __tablename__ = "security_scans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    risk_level: Mapped[str] = mapped_column(String(20), default="low")  # low, medium, high, critical
    findings: Mapped[list] = mapped_column(JSON, default=list)
    recommendations: Mapped[list] = mapped_column(JSON, default=list)
    ai_analysis: Mapped[str] = mapped_column(Text, nullable=True)
    auto_remediated: Mapped[bool] = mapped_column(Boolean, default=False)
    remediation_log: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
