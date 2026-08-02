from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base, utcnow
from .common import gen_id


class Ticket(Base):
    """A support request owned by one tenant. AI-assisted lifecycle."""

    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # new | open | pending | resolved | closed | escalated
    status: Mapped[str] = mapped_column(String(20), default="new", nullable=False, index=True)
    # low | medium | high | urgent
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    classification: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    messages: Mapped[list["TicketMessage"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at"
    )
    created_by: Mapped[Optional["User"]] = relationship(foreign_keys=[created_by_id])
    assigned_agent: Mapped[Optional["User"]] = relationship(foreign_keys=[assigned_agent_id])

    def __repr__(self) -> str:
        return f"<Ticket {self.subject} [{self.status}]>"


class TicketMessage(Base):
    """One turn in a ticket conversation. sender: user | ai | system."""

    __tablename__ = "ticket_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sender: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    sender_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    ticket: Mapped["Ticket"] = relationship(back_populates="messages")
    sender_user: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<TicketMessage {self.sender} on {self.ticket_id}>"
