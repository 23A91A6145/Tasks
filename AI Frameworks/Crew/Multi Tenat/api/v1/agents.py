from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...agents.engine import engine_status
from ...api.deps import get_workspace_membership, require_role
from ...core.database import get_db
from ...core.permissions import ROLE_ADMIN
from ...models import AgentConfig, Membership, Organization
from ...schemas.agents import AgentConfigOut, AgentConfigUpdate

router = APIRouter(prefix="/workspaces/{slug}/agents", tags=["agents"])

DEFAULT_AGENTS = [
    {
        "key": "manager",
        "name": "Support Manager",
        "role_description": "Coordinates the crew, delegates tasks and decides on human handoff.",
    },
    {
        "key": "router",
        "name": "Ticket Router",
        "role_description": "Classifies every ticket and assigns a priority.",
    },
    {
        "key": "knowledge",
        "name": "Knowledge Agent",
        "role_description": "Retrieves the most relevant tenant knowledge for each ticket.",
    },
    {
        "key": "support",
        "name": "Support Agent",
        "role_description": "Drafts grounded, professional customer replies.",
    },
    {
        "key": "escalation",
        "name": "Escalation Agent",
        "role_description": "Decides when a human teammate must take over.",
    },
    {
        "key": "report",
        "name": "Report Agent",
        "role_description": "Writes internal summaries and resolution notes.",
    },
]


def ensure_default_agents(db: Session, organization_id: str) -> list[AgentConfig]:
    existing = db.execute(
        select(AgentConfig).where(AgentConfig.organization_id == organization_id)
    ).scalars().all()
    if existing:
        return existing
    created = []
    for item in DEFAULT_AGENTS:
        config = AgentConfig(
            organization_id=organization_id,
            key=item["key"],
            name=item["name"],
            role_description=item["role_description"],
            enabled=True,
        )
        db.add(config)
        created.append(config)
    db.flush()
    return created


@router.get("", response_model=list[AgentConfigOut])
def list_agents(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> list[AgentConfigOut]:
    agents = ensure_default_agents(db, membership.organization_id)
    db.commit()
    agents = db.execute(
        select(AgentConfig)
        .where(AgentConfig.organization_id == membership.organization_id)
        .order_by(AgentConfig.created_at)
    ).scalars().all()
    return [AgentConfigOut.model_validate(agent) for agent in agents]


@router.get("/engine", response_model=dict)
def get_engine_status(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> dict:
    return engine_status()


@router.patch("/{agent_key}", response_model=AgentConfigOut)
def update_agent(
    slug: str,
    agent_key: str,
    data: AgentConfigUpdate,
    membership: Membership = Depends(require_role(ROLE_ADMIN)),
    db: Session = Depends(get_db),
) -> AgentConfigOut:
    agent = db.execute(
        select(AgentConfig).where(
            AgentConfig.organization_id == membership.organization_id,
            AgentConfig.key == agent_key,
        )
    ).scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found in this workspace")
    if data.name is not None:
        agent.name = data.name
    if data.role_description is not None:
        agent.role_description = data.role_description
    if data.llm_model is not None:
        agent.llm_model = data.llm_model
    if data.enabled is not None:
        agent.enabled = data.enabled
    from ...services import audit

    audit.log_activity(
        db,
        organization_id=membership.organization_id,
        user_id=membership.user_id,
        action="agent.updated",
        entity_type="agent",
        entity_id=agent.id,
        metadata={"agent_key": agent.key, "enabled": agent.enabled},
    )
    db.commit()
    db.refresh(agent)
    return AgentConfigOut.model_validate(agent)
