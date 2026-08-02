from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Table, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base, utcnow
from .common import gen_id


document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", String(36), ForeignKey("knowledge_documents.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("knowledge_tags.id", ondelete="CASCADE"), primary_key=True),
)


class KnowledgeDocument(Base):
    """A single uploaded / ingested document inside one tenant's knowledge base."""

    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    uploaded_by_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    # upload | url | faq
    source_type: Mapped[str] = mapped_column(String(20), default="upload", nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), default="txt", nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # queued | processing | ready | failed
    status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False, index=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stored_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    tags: Mapped[list["KnowledgeTag"]] = relationship(
        secondary=document_tags, back_populates="documents"
    )
    uploaded_by: Mapped[Optional["User"]] = relationship()

    def __repr__(self) -> str:
        return f"<KnowledgeDocument {self.filename} ({self.status})>"


class KnowledgeTag(Base):
    __tablename__ = "knowledge_tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=gen_id)
    organization_id: Mapped[str] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    documents: Mapped[list["KnowledgeDocument"]] = relationship(
        secondary=document_tags, back_populates="tags"
    )
