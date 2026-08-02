"""Flow run persistence helpers — the checkpoint engine.

Every flow writes its state into ``FlowRun.checkpoint``. A run can be paused
(``awaiting_approval``), resumed, approved or rejected through the API,
and rebuilt from its checkpoint on restart — this is what makes flows
"long-running" and resumable.
"""

from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import FlowRun, Organization, User


def create_run(
    db: Session,
    organization: Organization,
    flow_key: str,
    input_data: dict[str, Any],
    user: Optional[User] = None,
) -> FlowRun:
    run = FlowRun(
        organization_id=organization.id,
        flow_key=flow_key,
        status="running",
        current_step="start",
        input_data=input_data,
        checkpoint={},
        output_data={},
        created_by_id=user.id if user else None,
    )
    db.add(run)
    db.flush()
    return run


def save(db: Session, run: FlowRun) -> FlowRun:
    db.flush()
    return run


def set_status(db: Session, run: FlowRun, status: str) -> FlowRun:
    run.status = status
    db.flush()
    return run


def set_step(db: Session, run: FlowRun, step: str) -> FlowRun:
    run.current_step = step
    db.flush()
    return run


def set_output(db: Session, run: FlowRun, **fields: Any) -> FlowRun:
    run.output_data = {**run.output_data, **fields}
    db.flush()
    return run


def get_run(db: Session, organization_id: str, run_id: str) -> FlowRun:
    run = db.execute(
        select(FlowRun).where(
            FlowRun.id == run_id,
            FlowRun.organization_id == organization_id,
        )
    ).scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="Flow run not found in this workspace")
    return run


def list_runs(db: Session, organization_id: str, limit: int = 30) -> list[FlowRun]:
    return db.execute(
        select(FlowRun)
        .where(FlowRun.organization_id == organization_id)
        .order_by(FlowRun.created_at.desc())
        .limit(limit)
    ).scalars().all()
