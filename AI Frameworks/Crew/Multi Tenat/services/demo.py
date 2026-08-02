"""One-click demo provisioning — the project works with zero account/setup.

``POST /api/v1/auth/demo`` returns fresh tokens for the shared demo workspace
and guarantees it is provisioned on first call, so the whole product is
demonstrable on an empty database without signing up. Re-running is idempotent
and self-healing: baseline content (FAQ, tickets, agents, widget, webhook,
flow run, job, usage history) is replenished if a visitor deleted it.
"""

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.permissions import ROLE_OWNER
from ..core.security import hash_password
from ..models import (
    FlowRun,
    Job,
    KnowledgeDocument,
    Membership,
    Organization,
    Ticket,
    TicketMessage,
    UsageRecord,
    User,
)
from ..services import audit, knowledge_service, webhooks
from .workspace_service import unique_slug

DEMO_EMAIL = "owner@demo.com"
DEMO_PASSWORD = "demo-password-123"
DEMO_FULL_NAME = "Alex Owner"
DEMO_WORKSPACE = "Acme Support"

SAMPLE_FAQ = """Q: How do I reset my password?
A: Go to the login page, click "Forgot password", enter your email and follow the link you receive. Passwords expire every 90 days.

Q: Where do I find my invoice?
A: Invoices are available under Settings > Billing > Invoices. PDF copies are emailed to the workspace owner every month.

Q: How do I add a teammate?
A: Go to Users, click "Invite", enter their email and choose a role. They must have an account first.

Q: Can I cancel my subscription at any time?
A: Yes. Go to Billing and click "Cancel plan". You keep access until the end of the billing period.

Q: Why is my account locked?
A: Accounts lock after 5 failed login attempts. Use the password reset flow or contact your workspace admin to unlock it.

Q: What is your refund policy?
A: We offer full refunds within 30 days of purchase. Returns are accepted for all items.

Q: Do you support dark mode?
A: Yes. Toggle appearance from your profile menu.

Q: Which payment methods do you accept?
A: We accept all major credit cards, debit cards and PayPal.
"""

# subject, body, priority, status, classification, ai_summary
SAMPLE_TICKETS = [
    {
        "subject": "Can't log in after password change",
        "body": "Hi, I changed my password this morning and now the login page says my account is locked. I really need access before the end of the day. Please help!",
        "priority": "high",
        "status": "open",
        "classification": "account_access",
        "ai_summary": "User changed their password and is now locked out. Advise using the forgot-password flow and verify email ownership.",
        "ai_reply": "Sorry about that! Use the 'Forgot password' link on the login page to reset it, then check your inbox. You should be back in within a minute.",
    },
    {
        "subject": "Where is my latest invoice?",
        "body": "I need to download the invoice for this month for accounting. Can you point me to where it is?",
        "priority": "medium",
        "status": "new",
        "classification": "billing",
        "ai_summary": "",
        "ai_reply": "",
    },
    {
        "subject": "Refund request for duplicate charge",
        "body": "I was charged twice this month. Please refund the duplicate payment of $49.",
        "priority": "medium",
        "status": "resolved",
        "classification": "billing",
        "ai_summary": "Duplicate charge confirmed; refund of $49 issued. User informed.",
        "ai_reply": "You were right — the charge was duplicated. A refund of $49 has been issued and will appear in 3–5 business days. Sorry for the hassle!",
    },
    {
        "subject": "Outage on our help page",
        "body": "Our embedded help page is timing out for customers in the EU. Is this a known issue?",
        "priority": "urgent",
        "status": "escalated",
        "classification": "infrastructure",
        "ai_summary": "Escalated to the platform team — EU region latency suspected. On-call engineer notified.",
        "ai_reply": "",
    },
]


def _ensure_user(db: Session) -> User:
    user = db.execute(select(User).where(User.email == DEMO_EMAIL)).scalar_one_or_none()
    if user is None:
        user = User(
            email=DEMO_EMAIL,
            password_hash=hash_password(DEMO_PASSWORD),
            full_name=DEMO_FULL_NAME,
        )
        db.add(user)
        db.flush()
    return user


def _ensure_workspace(db: Session) -> Organization:
    org = db.execute(
        select(Organization).where(Organization.name == DEMO_WORKSPACE)
    ).scalar_one_or_none()
    if org is None:
        org = Organization(name=DEMO_WORKSPACE, slug=unique_slug(db, DEMO_WORKSPACE))
        db.add(org)
        db.flush()
    return org


def _ensure_baseline(db: Session, org: Organization, user: User) -> None:
    has_knowledge = db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.organization_id == org.id)
    ).first()
    if has_knowledge is None:
        knowledge_service.ingest_faq(
            db,
            organization=org,
            name="Acme Support FAQ",
            content=SAMPLE_FAQ,
            uploaded_by_id=user.id,
            tags=["faq", "account", "billing", "refund"],
        )

    existing = db.execute(
        select(Ticket).where(Ticket.organization_id == org.id)
    ).scalars().all()
    by_subject = {t.subject for t in existing}
    for item in SAMPLE_TICKETS:
        if item["subject"] in by_subject:
            continue
        ticket = Ticket(
            organization_id=org.id,
            subject=item["subject"],
            body=item["body"],
            priority=item["priority"],
            status=item["status"],
            classification=item["classification"] or None,
            ai_summary=item["ai_summary"] or None,
            created_by_id=user.id,
            resolved_at=(
                datetime.now(timezone.utc) - timedelta(days=2)
                if item["status"] == "resolved"
                else None
            ),
        )
        db.add(ticket)
        db.flush()
        db.add(
            TicketMessage(
                ticket_id=ticket.id,
                sender="user",
                sender_user_id=user.id,
                content=item["body"],
            )
        )
        if item.get("ai_reply"):
            db.add(
                TicketMessage(
                    ticket_id=ticket.id,
                    sender="ai",
                    content=item["ai_reply"],
                )
            )

    from ..api.v1.agents import ensure_default_agents

    ensure_default_agents(db, org.id)

    settings = dict(org.settings or {})
    if not settings.get("widget_enabled"):
        settings["widget_enabled"] = True
    if not settings.get("widget_token"):
        settings["widget_token"] = secrets.token_urlsafe(32)
    org.settings = settings

    if not (settings.get("webhook_url") or org.settings.get("webhook_url")):
        webhooks.set_config(
            db,
            org,
            url="https://example.com/hooks/tenantdesk",
            secret="demo-secret",
            events=["ticket.created", "ticket.ai_handled", "flow.approved"],
        )

    if db.execute(select(FlowRun).where(FlowRun.organization_id == org.id)).first() is None:
        db.add(
            FlowRun(
                organization_id=org.id,
                flow_key="ticket",
                status="completed",
                current_step="done",
                input_data={
                    "subject": "Refund request for duplicate charge",
                    "priority": "medium",
                },
                checkpoint={"engine": "fallback", "classification": "billing"},
                output_data={
                    "draft": "A refund of $49 has been issued. It will appear in 3–5 business days.",
                    "escalate": False,
                },
                created_by_id=user.id,
            )
        )

    if db.execute(select(Job).where(Job.organization_id == org.id)).first() is None:
        now = datetime.now(timezone.utc)
        db.add(
            Job(
                organization_id=org.id,
                job_type="index_document",
                status="completed",
                label="Index refund policy",
                current_step="done",
                total_steps=4,
                progress=100,
                input_data={"filename": "refund-policy.md"},
                checkpoint={"chunks": 3},
                result={"chunks_indexed": 3, "documents": 1},
                created_by_id=user.id,
                started_at=now - timedelta(hours=3),
                finished_at=now - timedelta(hours=3) + timedelta(minutes=2),
            )
        )

    if db.execute(select(UsageRecord).where(UsageRecord.organization_id == org.id)).first() is None:
        now = datetime.now(timezone.utc)
        for day_back in range(14, -1, -1):
            day = now - timedelta(days=day_back)
            for _ in range(1 + (day_back % 3)):
                db.add(
                    UsageRecord(
                        organization_id=org.id,
                        user_id=user.id,
                        kind="flow" if day_back % 2 else "search",
                        model="fallback",
                        tokens_in=120 + day_back * 7,
                        tokens_out=80 + day_back * 5,
                        units=1,
                        created_at=day.replace(hour=10 + (day_back % 8), minute=0, second=0, microsecond=0),
                    )
                )


def ensure_demo(db: Session) -> User:
    """Provision the shared demo workspace (idempotent, self-healing) and return the owner."""
    user = _ensure_user(db)
    org = _ensure_workspace(db)

    member = db.execute(
        select(Membership).where(
            Membership.organization_id == org.id, Membership.user_id == user.id
        )
    ).scalar_one_or_none()
    if member is None:
        db.add(Membership(organization_id=org.id, user_id=user.id, role=ROLE_OWNER))
        audit.log_activity(
            db,
            organization_id=org.id,
            user_id=user.id,
            action="member.invited",
            entity_type="user",
            entity_id=user.id,
            metadata={"email": user.email, "role": ROLE_OWNER},
        )

    _ensure_baseline(db, org, user)
    db.commit()
    return user
