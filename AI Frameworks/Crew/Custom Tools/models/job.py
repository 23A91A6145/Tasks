"""Long-running background jobs (Volume 4.2).

State machine:
    queued → running → completed
    queued → running → paused → running (resume)
    queued → running → failed → queued (retry)

Progress and step data live in ``checkpoint`` so a job can be resumed from
where it stopped — even after a process restart.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base, utcnow
from .common import gen_id


class Job(Base):
    """A checkpointed long-running job owned by one tenant."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # index_document | crawl_website | weekly_report | batch_faq
    job_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    # queued | running | paused | completed | failed
    status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False, index=True)
    label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_step: Mapped[str] = mapped_column(String(80), default="start", nullable=False)
    total_steps: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    input_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    checkpoint: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    organization: Mapped["Organization"] = relationship()
    created_by: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<Job {self.job_type} [{self.status}] {self.progress}%>"
