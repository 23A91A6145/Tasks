"""Audit logging helper."""

from typing import Any, Optional

from sqlalchemy.orm import Session

from ..models import ActivityLog


def log_activity(
    db: Session,
    *,
    organization_id: Optional[str],
    user_id: Optional[str],
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> ActivityLog:
    entry = ActivityLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_json=metadata or {},
    )
    db.add(entry)
    db.flush()
    return entry
