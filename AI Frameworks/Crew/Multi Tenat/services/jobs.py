"""Long-running job runner (Volume 4.2).

Jobs are persisted in the ``jobs`` table with progress + checkpoint state so
they can be paused, resumed and retried. Each job type is a small function
that receives ``(db, organization, job)`` and mutates ``job.progress`` /
``job.checkpoint`` as it works.

Job types
---------
- ``index_document``  re-index one document through the RAG pipeline
- ``crawl_website``   crawl a public site and ingest pages as URL documents
- ``batch_faq``       ingest one or many FAQ entries in one job
- ``weekly_report``   build a Markdown digest of the last 7 days of usage
"""

from datetime import datetime, timedelta, timezone
import os
from typing import Callable, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models import Job, KnowledgeDocument, Organization, Ticket, UsageRecord, User
from ..services import audit, plans
from . import knowledge_service

MAX_CRAWL_PAGES = 50


# ─────────────────────────── persistence helpers ───────────────────────────


def create_job(
    db: Session,
    organization: Organization,
    job_type: str,
    input_data: dict,
    user: Optional[User] = None,
    label: Optional[str] = None,
) -> Job:
    job = Job(
        organization_id=organization.id,
        job_type=job_type,
        status="queued",
        current_step="queued",
        input_data=input_data,
        label=label or input_data.get("label"),
        created_by_id=user.id if user else None,
    )
    db.add(job)
    db.flush()
    audit.log_activity(
        db,
        organization_id=organization.id,
        user_id=user.id if user else None,
        action="job.created",
        entity_type="job",
        entity_id=job.id,
        metadata={"job_type": job_type, "label": job.label},
    )
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, organization_id: str, job_id: str) -> Job:
    job = db.execute(
        select(Job).where(Job.id == job_id, Job.organization_id == organization_id)
    ).scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found in this workspace")
    return job


def list_jobs(db: Session, organization_id: str, limit: int = 50) -> list[Job]:
    return db.execute(
        select(Job)
        .where(Job.organization_id == organization_id)
        .order_by(Job.created_at.desc())
        .limit(min(limit, 100))
    ).scalars().all()


def _mark(db: Session, job: Job, status: str, step: Optional[str] = None) -> None:
    job.status = status
    if step:
        job.current_step = step
    if status == "running":
        job.started_at = job.started_at or datetime.now(timezone.utc)
    if status == "completed":
        job.progress = 100
        job.finished_at = datetime.now(timezone.utc)
    if status == "failed":
        job.finished_at = datetime.now(timezone.utc)
    db.add(job)
    db.commit()


def _progress(db: Session, job: Job, progress: int, step: str, checkpoint: Optional[dict] = None) -> None:
    job.progress = max(0, min(100, progress))
    job.current_step = step
    if checkpoint is not None:
        job.checkpoint = {**job.checkpoint, **checkpoint}
    db.add(job)
    db.commit()


# ─────────────────────────── job implementations ───────────────────────────


def _run_index_document(db: Session, org: Organization, job: Job) -> None:
    doc = db.get(KnowledgeDocument, job.input_data.get("document_id"))
    if doc is None or doc.organization_id != org.id:
        raise RuntimeError("Document not found in this workspace")

    _mark(db, job, "running", "reading document")
    text = knowledge_service.load_persisted_text(doc)
    if not text:
        raise RuntimeError("No stored text available for this document — re-upload it to re-index")
    chunks = knowledge_service.chunk_text(text)
    job.total_steps = len(chunks)

    from ..services.embeddings import get_embedder
    from ..services.vector import VectorPoint, get_vector_store

    embedder = get_embedder()
    store = get_vector_store()
    namespace = org.id

    store.delete_document(namespace, doc.id)
    points = []
    for i, chunk in enumerate(chunks):
        vector = embedder.embed([chunk])[0]
        points.append(
            VectorPoint(
                id=f"{doc.id}:{i}",
                document_id=doc.id,
                chunk_index=i,
                text=chunk,
                vector=vector,
                metadata={"filename": doc.filename, "source_type": doc.source_type},
            )
        )
        _progress(db, job, round((i + 1) / max(len(chunks), 1) * 100), "embedding chunks")
    store.upsert(namespace, points)

    doc.chunk_count = len(points)
    doc.status = "ready" if points else "failed"
    if not points:
        doc.error = "No searchable text extracted from this document."
    db.add(doc)
    job.result = {"document_id": doc.id, "chunks": len(points), "filename": doc.filename}
    _mark(db, job, "completed", "done")


def _run_crawl_website(db: Session, org: Organization, job: Job) -> None:
    start_url = job.input_data.get("url", "").strip()
    max_pages = int(job.input_data.get("max_pages") or 10)
    max_pages = min(max_pages, MAX_CRAWL_PAGES)

    if not start_url:
        raise RuntimeError("A start URL is required for website crawling")

    from ..core.urlsafety import validate_public_url

    try:
        start_url = validate_public_url(start_url)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

    import re

    import httpx
    import trafilatura

    visited: list[str] = list(job.checkpoint.get("visited", []))
    pending: list[str] = list(job.checkpoint.get("pending", [start_url]))
    host = re.sub(r"^[a-z]+://", "", start_url).split("/")[0]

    _mark(db, job, "running", "crawling")
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        while pending and len(visited) < max_pages:
            url = pending.pop(0)
            if url in visited:
                continue
            try:
                resp = client.get(url, headers={"User-Agent": "TenantDeskCrawler/1.0"})
                # never let a redirect to a private/loopback host bypass the SSRF guard
                validate_public_url(str(resp.url))
                text = trafilatura.extract(resp.text) if resp.status_code == 200 else None
            except Exception:
                text = None

            visited.append(url)
            if text and len(text.strip()) > 50:
                plans.check_knowledge_quota(db, org)
                filename = url.rstrip("/").split("/")[-1] or "webpage"
                doc = knowledge_service.ingest_text(
                    db,
                    organization=org,
                    filename=f"{filename}.md",
                    text=text,
                    source_type="url",
                    file_type="url",
                    source_url=url,
                )
                job.result.setdefault("ingested", []).append({"url": url, "document_id": doc.id})

            for link in re.findall(r'href="(https?://[^"]+)"', text or ""):
                if host in link and link not in visited and link not in pending and len(pending) < max_pages:
                    pending.append(link)

            _progress(
                db,
                job,
                round(len(visited) / max_pages * 100),
                f"crawled {len(visited)}/{max_pages}",
                {"visited": visited, "pending": pending[:MAX_CRAWL_PAGES]},
            )

    job.result["pages_crawled"] = len(visited)
    _mark(db, job, "completed", "done")


def _run_batch_faq(db: Session, org: Organization, job: Job) -> None:
    items = job.input_data.get("items", [])
    if not items and job.input_data.get("name") and job.input_data.get("content"):
        items = [{"name": job.input_data["name"], "content": job.input_data["content"]}]
    if not items:
        raise RuntimeError("No FAQ items supplied")

    job.total_steps = len(items)
    _mark(db, job, "running", "ingesting FAQs")
    created = []
    for i, item in enumerate(items):
        plans.check_knowledge_quota(db, org)
        doc = knowledge_service.ingest_faq(
            db,
            organization=org,
            name=str(item.get("name") or f"FAQ {i + 1}"),
            content=str(item.get("content") or ""),
        )
        created.append({"name": doc.filename, "document_id": doc.id})
        _progress(db, job, round((i + 1) / len(items) * 100), f"ingested {i + 1}/{len(items)}")
    job.result = {"documents": created, "count": len(created)}
    _mark(db, job, "completed", "done")


def _run_weekly_report(db: Session, org: Organization, job: Job) -> None:
    from ..services import usage
    from ..services.analytics import ticket_metrics

    _mark(db, job, "running", "aggregating usage")
    since = datetime.now(timezone.utc) - timedelta(days=7)
    totals = usage.workspace_totals(db, org.id)

    requests = sum(v["calls"] for v in totals.values())
    tokens = sum(v["tokens_in"] for v in totals.values()) + sum(v["tokens_out"] for v in totals.values())

    new_tickets = db.execute(
        select(Ticket).where(Ticket.organization_id == org.id, Ticket.created_at >= since)
    ).scalars().all()
    resolved = [t for t in new_tickets if t.status in ("resolved", "closed")]

    docs = db.execute(
        select(KnowledgeDocument).where(
            KnowledgeDocument.organization_id == org.id, KnowledgeDocument.created_at >= since
        )
    ).scalars().all()
    chunk_count = sum(d.chunk_count for d in docs)

    _progress(db, job, 60, "writing report")
    report = (
        f"# Weekly AI Support Report — {org.name}\n\n"
        f"Period: {since.strftime('%Y-%m-%d')} → {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
        f"## AI usage\n\n"
        f"- **{requests}** AI requests (LLM / embeddings / searches)\n"
        f"- **{tokens:,}** tokens processed\n\n"
        f"## Tickets\n\n"
        f"- **{len(new_tickets)}** new tickets\n"
        f"- **{len(resolved)}** resolved or closed\n\n"
        f"## Knowledge\n\n"
        f"- **{len(docs)}** documents added\n"
        f"- **{chunk_count}** chunks indexed\n\n"
        f"_Generated by the Report Agent.\n"
    )
    _progress(db, job, 90, "saving report")
    job.result = {"report_markdown": report, "period_days": 7, "requests": requests, "tokens": tokens}
    _mark(db, job, "completed", "done")


_HANDLERS: dict[str, Callable[[Session, Organization, Job], None]] = {
    "index_document": _run_index_document,
    "crawl_website": _run_crawl_website,
    "batch_faq": _run_batch_faq,
    "weekly_report": _run_weekly_report,
}


# ─────────────────────────── execution ───────────────────────────


def run_job(db: Session, job_id: str) -> None:
    """Execute a job synchronously on the given session.

    Safe to re-run: a failed job is retried from its checkpoint, and a
    completed job is a no-op. Production deployments can swap this for a real
    queue (Redis/Celery or Dramatiq) — the persistence + checkpoint contract
    stays identical.
    """
    job = db.execute(select(Job).where(Job.id == job_id)).scalar_one_or_none()
    if job is None or job.status == "completed":
        return
    handler = _HANDLERS.get(job.job_type)
    if handler is None:
        job.error = f"Unknown job type: {job.job_type}"
        _mark(db, job, "failed", "error")
        return
    org = db.get(Organization, job.organization_id)
    try:
        handler(db, org, job)
    except Exception as exc:
        job = db.execute(select(Job).where(Job.id == job_id)).scalar_one_or_none()
        if job is not None:
            job.status = "failed"
            job.error = str(exc)
            job.finished_at = datetime.now(timezone.utc)
            db.add(job)
            db.commit()


def retry_job(db: Session, organization_id: str, job_id: str) -> Job:
    job = get_job(db, organization_id, job_id)
    if job.status == "running":
        raise HTTPException(status_code=409, detail="Job is already running")
    job.status = "queued"
    job.error = None
    job.current_step = "queued"
    job.progress = 0
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, organization_id: str, job_id: str) -> Job:
    job = get_job(db, organization_id, job_id)
    db.delete(job)
    db.commit()
    return job


# ─────────────────────────── public helpers ───────────────────────────


def queue_and_run(db: Session, organization: Organization, job_type: str, input_data: dict, user=None, label=None) -> Job:
    """Create a job and run it (inline by default, or leave it queued).

    Set JOBS_INLINE=0 to run jobs from a background worker instead — the
    persistence + checkpoint contract stays identical, so swapping between
    inline, a polling worker, or Redis/Celery never touches the API.
    """
    job = create_job(db, organization, job_type, input_data, user=user, label=label)
    if os.environ.get("JOBS_INLINE", "1") != "0":
        run_job(db, job.id)
        db.refresh(job)
    return job


# ─────────────────────────── background worker ───────────────────────────


def run_worker(interval_seconds: int = 2) -> None:
    """Poll for queued jobs and run them. Compatible with a DB-backed queue.

    Production: run under `docker compose --profile worker up`. Jobs created
    with JOBS_INLINE=0 land in the queue; the worker claims and executes them
    with the same checkpoint/retry semantics as inline runs.
    """
    from ..core.database import SessionLocal, init_db

    import time

    init_db()
    print("[jobs] worker started — polling for queued jobs every", interval_seconds, "s")
    while True:
        try:
            db: Session = SessionLocal()
            try:
                queued = db.execute(
                    select(Job).where(Job.status == "queued").order_by(Job.created_at.asc()).limit(10)
                ).scalars().all()
                for job in queued:
                    print(f"[jobs] running {job.id} ({job.job_type})")
                    run_job(db, job.id)
            finally:
                db.close()
        except Exception as exc:  # keep the worker alive on transient DB errors
            print(f"[jobs] worker error: {exc}")
        time.sleep(interval_seconds)
