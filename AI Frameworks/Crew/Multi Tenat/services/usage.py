"""Usage metering — feeds plan limits (Vol 4) and analytics."""

from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import UsageRecord


def track(
    db: Session,
    *,
    organization_id: str,
    kind: str,
    model: Optional[str] = None,
    tokens_in: int = 0,
    tokens_out: int = 0,
    units: int = 1,
    user_id: Optional[str] = None,
    meta: Optional[dict[str, Any]] = None,
) -> UsageRecord:
    record = UsageRecord(
        organization_id=organization_id,
        user_id=user_id,
        kind=kind,
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        units=units,
        meta_json=meta or {},
    )
    db.add(record)
    db.flush()
    return record


def workspace_totals(db: Session, organization_id: str) -> dict:
    """Aggregate usage counts per kind for a tenant."""
    rows = db.execute(
        select(
            UsageRecord.kind,
            func.count(UsageRecord.id),
            func.coalesce(func.sum(UsageRecord.units), 0),
            func.coalesce(func.sum(UsageRecord.tokens_in), 0),
            func.coalesce(func.sum(UsageRecord.tokens_out), 0),
        )
        .where(UsageRecord.organization_id == organization_id)
        .group_by(UsageRecord.kind)
    ).all()
    return {
        kind: {
            "calls": count,
            "units": units,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
        }
        for kind, count, units, tokens_in, tokens_out in rows
    }
