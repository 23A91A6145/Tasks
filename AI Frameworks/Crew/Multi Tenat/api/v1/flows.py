from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...api.deps import get_current_user, get_workspace_membership, require_role
from ...core.database import get_db
from ...core.permissions import ROLE_MANAGER
from ...models import Membership, Organization, Ticket, User
from ...schemas.flows import FlowResumeRequest, FlowRunOut, FlowTriggerRequest
from ...flows import runner as flow_runner

router = APIRouter(prefix="/workspaces/{slug}/flows", tags=["flows"])


@router.get("", response_model=list[FlowRunOut])
def list_flow_runs(
    slug: str,
    limit: int = Query(default=30, ge=1, le=100),
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> list[FlowRunOut]:
    runs = flow_runner.list_runs(db, membership.organization_id, limit=limit)
    return [FlowRunOut.model_validate(run) for run in runs]


@router.get("/{run_id}", response_model=FlowRunOut)
def get_flow_run(
    slug: str,
    run_id: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> FlowRunOut:
    run = flow_runner.get_run(db, membership.organization_id, run_id)
    return FlowRunOut.model_validate(run)


@router.post("/{run_id}/resume", response_model=FlowRunOut)
def resume_flow_run(
    slug: str,
    run_id: str,
    data: FlowResumeRequest,
    membership: Membership = Depends(require_role(ROLE_MANAGER)),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FlowRunOut:
    """Human checkpoint approval: approve publishes the AI draft, reject discards it."""
    from ...flows import ticket_flow

    run = flow_runner.get_run(db, membership.organization_id, run_id)
    if run.status not in ("awaiting_approval", "approved", "rejected"):
        raise HTTPException(status_code=409, detail=f"Flow is not awaiting approval (status={run.status})")
    organization = db.get(Organization, membership.organization_id)
    try:
        updated = ticket_flow.resume_ticket_flow(db, organization, run, data.approved, user=user)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return FlowRunOut.model_validate(updated)


@router.post("/trigger", response_model=FlowRunOut, status_code=201)
def trigger_flow(
    slug: str,
    data: FlowTriggerRequest,
    membership: Membership = Depends(require_role(ROLE_MANAGER)),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FlowRunOut:
    organization = db.get(Organization, membership.organization_id)
    ticket = db.get(Ticket, data.ticket_id)
    if ticket is None or ticket.organization_id != organization.id:
        raise HTTPException(status_code=404, detail="Ticket not found in this workspace")

    from ...flows import escalation_flow, feedback_flow

    if data.flow_key == "escalation":
        run = escalation_flow.run_escalation_flow(
            db, organization, ticket, user=user, reason=data.reason or ""
        )
    elif data.flow_key == "feedback":
        if data.rating is None:
            raise HTTPException(status_code=422, detail="rating (1-5) is required for the feedback flow")
        run = feedback_flow.run_feedback_flow(
            db, organization, ticket, data.rating, comment=data.comment or "", user=user
        )
    else:  # pragma: no cover — schema restricts flow_key
        raise HTTPException(status_code=422, detail="Unsupported flow")
    return FlowRunOut.model_validate(run)
