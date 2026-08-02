from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base, utcnow
from .common import gen_id


class UsageRecord(Base):
    """Metered usage per tenant — feeds plans (Vol 4) and analytics."""

    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # llm | embed | search | flow
    kind: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    model: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    tokens_in: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    units: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    meta_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<UsageRecord {self.kind} x{self.units} ({self.organization_id})>"
