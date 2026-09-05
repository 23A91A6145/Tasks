import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ResearchProjectDB(Base):
    __tablename__ = "research_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    runs = relationship("ResearchRunDB", back_populates="project", cascade="all, delete-orphan")

class ResearchRunDB(Base):
    __tablename__ = "research_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("research_projects.id"), nullable=True)
    query = Column(Text, nullable=False)
    mode = Column(String(50), default="deep")
    status = Column(String(50), default="pending")
    plan_json = Column(JSON, nullable=True)
    final_report_markdown = Column(Text, nullable=True)
    report_json = Column(JSON, nullable=True)
    critique_score = Column(Integer, nullable=True)
    metrics_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    project = relationship("ResearchProjectDB", back_populates="runs")
    sources = relationship("SourceDB", back_populates="run", cascade="all, delete-orphan")
    claims = relationship("AtomicClaimDB", back_populates="run", cascade="all, delete-orphan")

class SourceDB(Base):
    __tablename__ = "sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("research_runs.id"), nullable=False)
    title = Column(String(512), nullable=False)
    url = Column(Text, nullable=False)
    source_type = Column(String(50), default="web")
    author = Column(String(255), nullable=True)
    published_date = Column(String(50), nullable=True)
    domain = Column(String(255), nullable=False)
    snippet = Column(Text, nullable=False)
    full_text = Column(Text, nullable=True)
    reliability_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("ResearchRunDB", back_populates="sources")

class AtomicClaimDB(Base):
    __tablename__ = "atomic_claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("research_runs.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.85)
    verification_status = Column(String(50), default="verified")
    source_id = Column(String(36), nullable=True)
    evidence_snippet = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("ResearchRunDB", back_populates="claims")
