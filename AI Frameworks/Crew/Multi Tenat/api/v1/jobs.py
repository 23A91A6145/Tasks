from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...api.deps import get_current_user, get_workspace_membership, require_role
from ...core.database import get_db
from ...core.permissions import ROLE_AGENT
from ...models import Membership, Organization, User
from ...schemas.jobs import JobCreate, JobOut
from ...services import audit, jobs as job_service

router = APIRouter(prefix="/workspaces/{slug}/jobs", tags=["jobs"])

JOB_META = {
    "index_document": {"label": "Re-index document", "needs": "document_id"},
    "crawl_website": {"label": "Crawl website", "needs": "url"},
    "batch_faq": {"label": "Batch FAQ import", "needs": "items"},
    "weekly_report": {"label": "Weekly report", "needs": ""},
}


@router.get("", response_model=list[JobOut])
def list_jobs(
    slug: str,
    limit: int = Query(default=50, ge=1, le=100),
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> list[JobOut]:
    jobs = job_service.list_jobs(db, membership.organization_id, limit=limit)
    return [JobOut.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    slug: str,
    job_id: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> JobOut:
    job = job_service.get_job(db, membership.organization_id, job_id)
    return JobOut.model_validate(job)


@router.post("", response_model=JobOut, status_code=201)
def create_job(
    slug: str,
    data: JobCreate,
    membership: Membership = Depends(require_role(ROLE_AGENT)),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobOut:
    """Queue and run a long-running job (indexing, crawling, reports, FAQ batches)."""
    organization = db.get(Organization, membership.organization_id)

    input_data: dict = {"label": data.label}
    if data.job_type == "index_document":
        if not data.document_id:
            raise HTTPException(status_code=422, detail="document_id is required to re-index a document")
        input_data["document_id"] = data.document_id
    elif data.job_type == "crawl_website":
        if not data.url:
            raise HTTPException(status_code=422, detail="url is required to crawl a website")
        input_data["url"] = data.url
        input_data["max_pages"] = data.max_pages or 10
    elif data.job_type == "batch_faq":
        input_data["items"] = data.items or []
        if data.name and data.content:
            input_data["items"].append({"name": data.name, "content": data.content})
    elif data.job_type == "weekly_report":
        pass

    job = job_service.queue_and_run(
        db,
        organization,
        data.job_type,
        input_data,
        user=user,
        label=data.label or JOB_META[data.job_type]["label"],
    )
    return JobOut.model_validate(job)


@router.post("/{job_id}/retry", response_model=JobOut)
def retry_job(
    slug: str,
    job_id: str,
    membership: Membership = Depends(require_role(ROLE_AGENT)),
    db: Session = Depends(get_db),
) -> JobOut:
    job = job_service.retry_job(db, membership.organization_id, job_id)
    audit.log_activity(
        db,
        organization_id=membership.organization_id,
        user_id=membership.user_id,
        action="job.retried",
        entity_type="job",
        entity_id=job.id,
        metadata={"job_type": job.job_type},
    )
    db.commit()
    job_service.run_job(db, job.id)
    db.refresh(job)
    return JobOut.model_validate(job)


@router.delete("/{job_id}", status_code=204)
def delete_job(
    slug: str,
    job_id: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> None:
    job = job_service.delete_job(db, membership.organization_id, job_id)
    audit.log_activity(
        db,
        organization_id=membership.organization_id,
        user_id=None,
        action="job.deleted",
        entity_type="job",
        entity_id=job.id,
        metadata={"job_type": job.job_type},
    )
    db.commit()

