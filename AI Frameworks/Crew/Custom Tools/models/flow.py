from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base, utcnow
from .common import gen_id


class FlowRun(Base):
    """A checkpointed long-running workflow instance for a tenant.

    State machine:
        running → awaiting_approval ⇄ approved / rejected → completed
        running → failed
    """

    __tablename__ = "flow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # ticket | escalation | feedback
    flow_key: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    # running | awaiting_approval | approved | rejected | completed | failed
    status: Mapped[str] = mapped_column(String(30), default="running", nullable=False, index=True)
    current_step: Mapped[str] = mapped_column(String(60), default="start", nullable=False)
    input_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    checkpoint: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    output_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    organization: Mapped["Organization"] = relationship()
    created_by: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<FlowRun {self.flow_key} [{self.status}]>"


class AgentConfig(Base):
    """Per-tenant AI crew member configuration."""

    __tablename__ = "agent_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    role_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    llm_model: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    organization: Mapped["Organization"] = relationship()

    def __repr__(self) -> str:
        return f"<AgentConfig {self.key} enabled={self.enabled}>"
