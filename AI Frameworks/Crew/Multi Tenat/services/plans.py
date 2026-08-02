"""Plans & usage limits (Volume 4.1).

Plan catalog + monthly-usage metering anchored to each workspace's creation
date. Every tenant pays the same code path — plan switching just changes the
limit numbers the enforcement helpers use.
"""

from datetime import datetime, time, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import KnowledgeDocument, Membership, Organization, UsageRecord

VALID_PLANS = ("free", "pro", "enterprise")

# requests_per_month: 0 = unlimited
PLANS: dict[str, dict] = {
    "free": {
        "name": "Free",
        "price_month": 0,
        "requests_per_month": 500,
        "knowledge_docs": 10,
        "seats": 5,
        "storage_mb": 100,
        "priority_processing": False,
        "advanced_analytics": False,
        "description": "For teams trying out AI support.",
    },
    "pro": {
        "name": "Pro",
        "price_month": 49,
        "requests_per_month": 5000,
        "knowledge_docs": 100,
        "seats": 50,
        "storage_mb": 2048,
        "priority_processing": True,
        "advanced_analytics": True,
        "description": "For growing support teams.",
    },
    "enterprise": {
        "name": "Enterprise",
        "price_month": 299,
        "requests_per_month": 0,
        "knowledge_docs": 0,
        "seats": 0,
        "storage_mb": 0,
        "priority_processing": True,
        "advanced_analytics": True,
        "description": "Unlimited usage for organizations at scale.",
    },
}

# Rough per-1M-token costs for the estimate shown in Analytics (gpt-4o-mini class).
COST_PER_MILLION = {"input": 0.15, "output": 0.60, "embedding": 0.02}


def plan_limits(plan: str) -> dict:
    return PLANS.get(plan, PLANS["free"])


def is_unlimited(value: int) -> bool:
    return value == 0


def period_start(org: Organization) -> datetime:
    """Start of the current monthly billing cycle, anchored to org.created_at."""
    now = datetime.now(timezone.utc)
    anchor = org.created_at.astimezone(timezone.utc) if org.created_at.tzinfo else org.created_at.replace(tzinfo=timezone.utc)
    anchor_day = min(anchor.day, 28)  # avoid overflow on short months

    def _first_of_month(dt: datetime) -> datetime:
        return dt.replace(day=anchor_day, hour=0, minute=0, second=0, microsecond=0)

    candidate = _first_of_month(now)
    if candidate <= now and candidate >= anchor.replace(day=1, hour=0, minute=0, second=0, microsecond=0):
        return candidate
    # fall back to the previous month
    previous = candidate.replace(day=1) - __import__("datetime").timedelta(days=1)
    return _first_of_month(previous)


def period_end(org: Organization) -> datetime:
    start = period_start(org)
    next_month = (start.replace(day=1) + __import__("datetime").timedelta(days=32)).replace(day=1)
    return next_month


def requests_this_month(db: Session, org: Organization) -> int:
    start = period_start(org)
    return int(
        db.execute(
            select(func.count(UsageRecord.id)).where(
                UsageRecord.organization_id == org.id,
                UsageRecord.created_at >= start,
            )
        ).scalar_one()
    )


def tokens_this_month(db: Session, org: Organization) -> dict:
    start = period_start(org)
    row = db.execute(
        select(
            func.coalesce(func.sum(UsageRecord.tokens_in), 0),
            func.coalesce(func.sum(UsageRecord.tokens_out), 0),
        ).where(UsageRecord.organization_id == org.id, UsageRecord.created_at >= start)
    ).one()
    return {"tokens_in": int(row[0]), "tokens_out": int(row[1]), "total": int(row[0] + row[1])}


def storage_usage(db: Session, org: Organization) -> dict:
    rows = db.execute(
        select(
            func.count(KnowledgeDocument.id),
            func.coalesce(func.sum(KnowledgeDocument.size_bytes), 0),
            func.coalesce(func.sum(KnowledgeDocument.chunk_count), 0),
        ).where(KnowledgeDocument.organization_id == org.id)
    ).one()
    return {"docs": int(rows[0]), "bytes": int(rows[1]), "chunks": int(rows[2])}


def seat_count(db: Session, org: Organization) -> int:
    return int(
        db.execute(
            select(func.count(Membership.id)).where(Membership.organization_id == org.id)
        ).scalar_one()
    )


def usage_vs_limits(db: Session, org: Organization) -> list[dict]:
    """Current usage against plan limits — drives the Billing page meters."""
    limits = plan_limits(org.plan)
    requests = requests_this_month(db, org)
    tokens = tokens_this_month(db, org)
    storage = storage_usage(db, org)
    seats = seat_count(db, org)

    items = [
        {
            "key": "requests",
            "label": "AI requests / month",
            "used": requests,
            "limit": limits["requests_per_month"],
            "unit": "requests",
            "note": "Reset on the workspace billing date",
        },
        {
            "key": "tokens",
            "label": "Tokens processed",
            "used": tokens["total"],
            "limit": 0,
            "unit": "tokens",
            "note": "Input + output across LLM calls",
        },
        {
            "key": "documents",
            "label": "Knowledge documents",
            "used": storage["docs"],
            "limit": limits["knowledge_docs"],
            "unit": "docs",
            "note": "Uploads, websites and FAQs",
        },
        {
            "key": "storage",
            "label": "Knowledge storage",
            "used": round(storage["bytes"] / (1024 * 1024), 1),
            "limit": limits["storage_mb"],
            "unit": "MB",
            "note": "Extracted text in the vector store",
        },
        {
            "key": "seats",
            "label": "Team seats",
            "used": seats,
            "limit": limits["seats"],
            "unit": "members",
            "note": "Active workspace members",
        },
    ]
    for item in items:
        limit = item["limit"]
        item["unlimited"] = is_unlimited(limit)
        item["percent"] = 0 if is_unlimited(limit) or limit == 0 else round(min(100, item["used"] / limit * 100), 1)
        item["remaining"] = "unlimited" if is_unlimited(limit) else max(0, limit - item["used"])
    return items


# ─────────────────────────── enforcement ───────────────────────────


def check_request_quota(db: Session, org: Organization) -> None:
    limits = plan_limits(org.plan)
    if is_unlimited(limits["requests_per_month"]):
        return
    used = requests_this_month(db, org)
    if used >= limits["requests_per_month"]:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Your {org.plan} plan's monthly AI request limit "
                f"({limits['requests_per_month']}) is used up. "
                "Upgrade the plan or wait for the next billing cycle."
            ),
        )


def check_knowledge_quota(db: Session, org: Organization) -> None:
    limits = plan_limits(org.plan)
    if is_unlimited(limits["knowledge_docs"]):
        return
    storage = storage_usage(db, org)
    if storage["docs"] >= limits["knowledge_docs"]:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Your {org.plan} plan allows {limits['knowledge_docs']} knowledge "
                "documents. Delete some or upgrade the plan."
            ),
        )


def check_seat_quota(db: Session, org: Organization) -> None:
    limits = plan_limits(org.plan)
    if is_unlimited(limits["seats"]):
        return
    if seat_count(db, org) >= limits["seats"]:
        raise HTTPException(
            status_code=429,
            detail=f"Your {org.plan} plan allows {limits['seats']} team seats. Upgrade the plan to add more.",
        )


def change_plan(db: Session, org: Organization, new_plan: str, by: Optional[str] = None) -> Organization:
    if new_plan not in VALID_PLANS:
        raise HTTPException(status_code=422, detail=f"Invalid plan. Choose from {list(VALID_PLANS)}")
    if new_plan == org.plan:
        raise HTTPException(status_code=409, detail=f"You are already on the {new_plan} plan")
    from ..services import audit

    audit.log_activity(
        db,
        organization_id=org.id,
        user_id=by,
        action="plan.changed",
        entity_type="organization",
        entity_id=org.id,
        metadata={"from": org.plan, "to": new_plan},
    )
    org.plan = new_plan
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def billing_summary(db: Session, org: Organization) -> dict:
    """Everything the Billing page needs in one call."""
    return {
        "plan": org.plan,
        "plan_details": plan_limits(org.plan),
        "period_start": period_start(org).isoformat(),
        "period_end": period_end(org).isoformat(),
        "items": usage_vs_limits(db, org),
        "all_plans": [
            {
                "key": key,
                "name": value["name"],
                "price_month": value["price_month"],
                "description": value["description"],
                "requests_per_month": value["requests_per_month"],
                "knowledge_docs": value["knowledge_docs"],
                "seats": value["seats"],
                "storage_mb": value["storage_mb"],
                "advanced_analytics": value["advanced_analytics"],
            }
            for key, value in PLANS.items()
        ],
    }
