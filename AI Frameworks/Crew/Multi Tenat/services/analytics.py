"""Monitoring & analytics (Volume 4.3).

Aggregates the usage/ticket/flow/knowledge tables into the series the
dashboard charts need. All queries are scoped to one organization_id —
tenant isolation is enforced here, never in the client.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import (
    ActivityLog,
    AgentConfig,
    FlowRun,
    KnowledgeDocument,
    Organization,
    Ticket,
    TicketMessage,
    UsageRecord,
)
from . import plans

_STATUSES = ("new", "open", "pending", "resolved", "closed", "escalated")


def _date_bucket(dt: datetime) -> str:
    dt = dt.astimezone(timezone.utc) if dt.tzinfo else dt
    return dt.strftime("%Y-%m-%d")


def _fill_series(start: datetime, buckets: dict[str, int]) -> list[dict]:
    days = []
    for i in range((datetime.now(timezone.utc).date() - start.date()).days + 1):
        day = start.date() + timedelta(days=i)
        key = day.strftime("%Y-%m-%d")
        days.append({"date": key, "count": int(buckets.get(key, 0))})
    return days


def summary(db: Session, org: Organization) -> dict:
    """KPI cards for the analytics dashboard."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)

    rows = db.execute(
        select(
            func.count(UsageRecord.id),
            func.coalesce(func.sum(UsageRecord.tokens_in), 0),
            func.coalesce(func.sum(UsageRecord.tokens_out), 0),
        ).where(UsageRecord.organization_id == org.id, UsageRecord.created_at >= month_start)
    ).one()
    requests, tokens_in, tokens_out = int(rows[0]), int(rows[1]), int(rows[2])

    cost = (
        tokens_in * plans.COST_PER_MILLION["input"] / 1_000_000
        + tokens_out * plans.COST_PER_MILLION["output"] / 1_000_000
    )

    open_tickets = int(
        db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.organization_id == org.id, Ticket.status.in_(("new", "open", "pending"))
            )
        ).scalar_one()
    )

    created_week = int(
        db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.organization_id == org.id, Ticket.created_at >= week_start
            )
        ).scalar_one()
    )
    resolved_week = int(
        db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.organization_id == org.id,
                Ticket.status.in_(("resolved", "closed")),
                Ticket.updated_at >= week_start,
            )
        ).scalar_one()
    )

    storage = plans.storage_usage(db, org)
    active_agents = int(
        db.execute(
            select(func.count(AgentConfig.id)).where(
                AgentConfig.organization_id == org.id, AgentConfig.enabled.is_(True)
            )
        ).scalar_one()
    )

    limits = plans.plan_limits(org.plan)
    req_limit = limits["requests_per_month"]
    request_percent = 0 if plans.is_unlimited(req_limit) else round(min(100, requests / req_limit * 100), 1)

    return {
        "requests_month": requests,
        "request_limit": req_limit,
        "request_percent": request_percent,
        "tokens_month": tokens_in + tokens_out,
        "est_cost_month": round(cost, 2),
        "tickets_open": open_tickets,
        "tickets_created_7d": created_week,
        "tickets_resolved_7d": resolved_week,
        "resolution_rate_7d": round(resolved_week / created_week * 100, 1) if created_week else 0,
        "knowledge_docs": storage["docs"],
        "knowledge_chunks": storage["chunks"],
        "active_agents": active_agents,
        "plan": org.plan,
    }


def usage_series(db: Session, org: Organization, days: int = 30) -> dict:
    start = datetime.now(timezone.utc) - timedelta(days=days - 1)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    rows = db.execute(
        select(
            UsageRecord.created_at,
            UsageRecord.kind,
            UsageRecord.tokens_in,
            UsageRecord.tokens_out,
        ).where(UsageRecord.organization_id == org.id, UsageRecord.created_at >= start)
    ).all()

    daily_total: dict[str, int] = {}
    daily_tokens: dict[str, int] = {}
    by_kind: dict[str, dict[str, int]] = {}
    for created, kind, tin, tout in rows:
        key = _date_bucket(created)
        daily_total[key] = daily_total.get(key, 0) + 1
        daily_tokens[key] = daily_tokens.get(key, 0) + tin + tout
        bucket = by_kind.setdefault(kind, {"calls": 0, "tokens": 0})
        bucket["calls"] += 1
        bucket["tokens"] += tin + tout

    return {
        "daily_requests": _fill_series(start, daily_total),
        "daily_tokens": _fill_series(start, daily_tokens),
        "by_kind": [{"kind": k, **v} for k, v in sorted(by_kind.items())],
        "total_requests": sum(daily_total.values()),
        "total_tokens": sum(daily_tokens.values()),
    }


def ticket_metrics(db: Session, org: Organization, days: int = 30) -> dict:
    start = datetime.now(timezone.utc) - timedelta(days=days - 1)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    tickets = db.execute(
        select(Ticket).where(Ticket.organization_id == org.id, Ticket.created_at >= start)
    ).scalars().all()

    by_status = {s: 0 for s in _STATUSES}
    by_priority = {"low": 0, "medium": 0, "high": 0, "urgent": 0}
    by_classification: dict[str, int] = {}
    daily_created: dict[str, int] = {}

    resolution_hours: list[float] = []
    for ticket in tickets:
        by_status[ticket.status] = by_status.get(ticket.status, 0) + 1
        by_priority[ticket.priority] = by_priority.get(ticket.priority, 0) + 1
        if ticket.classification:
            by_classification[ticket.classification] = by_classification.get(ticket.classification, 0) + 1
        daily_created[_date_bucket(ticket.created_at)] = daily_created.get(_date_bucket(ticket.created_at), 0) + 1
        if ticket.resolved_at and ticket.created_at:
            resolution_hours.append(
                (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
            )

    avg_resolution = round(sum(resolution_hours) / len(resolution_hours), 1) if resolution_hours else 0

    return {
        "daily_created": _fill_series(start, daily_created),
        "by_status": [{"status": k, "count": v} for k, v in by_status.items()],
        "by_priority": [{"priority": k, "count": v} for k, v in by_priority.items()],
        "by_classification": [{"classification": k, "count": v} for k, v in sorted(by_classification.items(), key=lambda x: -x[1])],
        "avg_resolution_hours": avg_resolution,
        "total": len(tickets),
    }


def knowledge_growth(db: Session, org: Organization, days: int = 30) -> dict:
    start = datetime.now(timezone.utc) - timedelta(days=days - 1)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    docs = db.execute(
        select(KnowledgeDocument.created_at, KnowledgeDocument.chunk_count).where(
            KnowledgeDocument.organization_id == org.id, KnowledgeDocument.created_at >= start
        )
    ).all()

    daily_added: dict[str, int] = {}
    daily_chunks: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for created, chunks in docs:
        key = _date_bucket(created)
        daily_added[key] = daily_added.get(key, 0) + 1
        daily_chunks[key] = daily_chunks.get(key, 0) + chunks

    by_source_rows = db.execute(
        select(KnowledgeDocument.source_type, func.count(KnowledgeDocument.id)).where(
            KnowledgeDocument.organization_id == org.id
        ).group_by(KnowledgeDocument.source_type)
    ).all()
    for source, count in by_source_rows:
        by_source[source] = int(count)

    return {
        "daily_added": _fill_series(start, daily_added),
        "daily_chunks": _fill_series(start, daily_chunks),
        "by_source": [{"source": k, "count": v} for k, v in by_source.items()],
    }


def agent_performance(db: Session, org: Organization, days: int = 30) -> dict:
    start = datetime.now(timezone.utc) - timedelta(days=days - 1)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    runs = db.execute(
        select(FlowRun).where(FlowRun.organization_id == org.id, FlowRun.created_at >= start)
    ).scalars().all()

    flows: dict[str, dict] = {}
    engine_counts: dict[str, int] = {}
    for run in runs:
        bucket = flows.setdefault(
            run.flow_key,
            {"flow": run.flow_key, "total": 0, "completed": 0, "awaiting_approval": 0, "rejected": 0, "failed": 0},
        )
        bucket["total"] += 1
        if run.status == "completed":
            bucket["completed"] += 1
        elif run.status == "awaiting_approval":
            bucket["awaiting_approval"] += 1
        elif run.status == "rejected":
            bucket["rejected"] += 1
        elif run.status == "failed":
            bucket["failed"] += 1
        engine = run.checkpoint.get("engine") or "n/a"
        engine_counts[engine] = engine_counts.get(engine, 0) + 1

    return {
        "flows": list(flows.values()),
        "engine_distribution": [{"engine": k, "count": v} for k, v in sorted(engine_counts.items(), key=lambda x: -x[1])],
        "total_runs": len(runs),
    }


def activity_series(db: Session, org: Organization, days: int = 30) -> dict:
    start = datetime.now(timezone.utc) - timedelta(days=days - 1)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    rows = db.execute(
        select(ActivityLog.created_at).where(
            ActivityLog.organization_id == org.id, ActivityLog.created_at >= start
        )
    ).all()
    buckets: dict[str, int] = {}
    for (created,) in rows:
        key = _date_bucket(created)
        buckets[key] = buckets.get(key, 0) + 1
    return {"daily_activity": _fill_series(start, buckets)}


def overview(db: Session, org: Organization) -> dict:
    """Combined payload for the analytics page (fewer round trips)."""
    return {
        "summary": summary(db, org),
        "usage": usage_series(db, org, days=30),
        "tickets": ticket_metrics(db, org, days=30),
        "knowledge": knowledge_growth(db, org, days=30),
        "agents": agent_performance(db, org, days=30),
    }
