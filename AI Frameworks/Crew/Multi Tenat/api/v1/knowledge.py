from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...api.deps import get_current_user, get_workspace_membership
from ...core.database import get_db
from ...models import KnowledgeDocument, KnowledgeTag, Membership, Organization, User, document_tags
from ...schemas.knowledge import (
    FAQIngest,
    KnowledgeDocumentOut,
    KnowledgeHit,
    KnowledgeSearchOut,
    KnowledgeSearchRequest,
    TagOut,
    TextIngest,
    URLIngest,
)
from ...services import audit, knowledge_service, plans, usage

router = APIRouter(prefix="/workspaces/{slug}/knowledge", tags=["knowledge"])


def _doc_out(doc: KnowledgeDocument) -> KnowledgeDocumentOut:
    return KnowledgeDocumentOut(
        id=doc.id,
        filename=doc.filename,
        source_type=doc.source_type,
        file_type=doc.file_type,
        source_url=doc.source_url,
        size_bytes=doc.size_bytes,
        status=doc.status,
        error=doc.error,
        chunk_count=doc.chunk_count,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        tags=[tag.name for tag in doc.tags],
    )


@router.get("", response_model=list[KnowledgeDocumentOut])
def list_documents(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> list[KnowledgeDocumentOut]:
    docs = (
        db.execute(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.organization_id == membership.organization_id)
            .order_by(KnowledgeDocument.created_at.desc())
        )
        .scalars()
        .all()
    )
    return [_doc_out(doc) for doc in docs]


@router.post("", response_model=KnowledgeDocumentOut, status_code=201)
def upload_document(
    slug: str,
    file: UploadFile = File(...),
    tags: str = Form(default=""),
    membership: Membership = Depends(get_workspace_membership),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeDocumentOut:
    organization = db.get(Organization, membership.organization_id)
    plans.check_knowledge_quota(db, organization)
    content = file.file.read()
    doc = knowledge_service.ingest_file(
        db,
        organization=organization,
        filename=file.filename or "document.txt",
        content=content,
        uploaded_by_id=user.id,
        tags=[t for t in tags.split(",") if t.strip()],
    )
    usage.track(
        db,
        organization_id=organization.id,
        user_id=user.id,
        kind="embed",
        units=max(1, doc.chunk_count),
        meta={"action": "knowledge.upload", "chunks": doc.chunk_count},
    )
    audit.log_activity(
        db,
        organization_id=organization.id,
        user_id=user.id,
        action="knowledge.uploaded",
        entity_type="knowledge_document",
        entity_id=doc.id,
        metadata={"filename": doc.filename, "chunks": doc.chunk_count},
    )
    db.commit()
    db.refresh(doc)
    return _doc_out(doc)


@router.post("/ingest-url", response_model=KnowledgeDocumentOut, status_code=201)
def ingest_url(
    slug: str,
    data: URLIngest,
    membership: Membership = Depends(get_workspace_membership),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeDocumentOut:
    organization = db.get(Organization, membership.organization_id)
    plans.check_knowledge_quota(db, organization)
    doc = knowledge_service.ingest_url(
        db, organization=organization, url=data.url, uploaded_by_id=user.id
    )
    usage.track(
        db,
        organization_id=organization.id,
        user_id=user.id,
        kind="embed",
        units=max(1, doc.chunk_count),
        meta={"action": "knowledge.url", "chunks": doc.chunk_count},
    )
    audit.log_activity(
        db,
        organization_id=organization.id,
        user_id=user.id,
        action="knowledge.url_ingested",
        entity_type="knowledge_document",
        entity_id=doc.id,
        metadata={"url": data.url, "chunks": doc.chunk_count},
    )
    db.commit()
    db.refresh(doc)
    return _doc_out(doc)


@router.post("/text", response_model=KnowledgeDocumentOut, status_code=201)
def ingest_text(
    slug: str,
    data: TextIngest,
    membership: Membership = Depends(get_workspace_membership),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeDocumentOut:
    organization = db.get(Organization, membership.organization_id)
    plans.check_knowledge_quota(db, organization)
    doc = knowledge_service.ingest_text(
        db,
        organization=organization,
        filename=data.name,
        text=data.content,
        source_type="faq" if "faq" in data.tags else "upload",
        uploaded_by_id=user.id,
        tags=data.tags,
    )
    usage.track(
        db,
        organization_id=organization.id,
        user_id=user.id,
        kind="embed",
        units=max(1, doc.chunk_count),
        meta={"action": "knowledge.text", "chunks": doc.chunk_count},
    )
    audit.log_activity(
        db,
        organization_id=organization.id,
        user_id=user.id,
        action="knowledge.text_created",
        entity_type="knowledge_document",
        entity_id=doc.id,
        metadata={"name": data.name, "chunks": doc.chunk_count},
    )
    db.commit()
    db.refresh(doc)
    return _doc_out(doc)


@router.post("/faq", response_model=KnowledgeDocumentOut, status_code=201)
def ingest_faq(
    slug: str,
    data: FAQIngest,
    membership: Membership = Depends(get_workspace_membership),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> KnowledgeDocumentOut:
    organization = db.get(Organization, membership.organization_id)
    plans.check_knowledge_quota(db, organization)
    doc = knowledge_service.ingest_faq(
        db,
        organization=organization,
        name=data.name,
        content=data.content,
        uploaded_by_id=user.id,
        tags=["faq"],
    )
    usage.track(
        db,
        organization_id=organization.id,
        user_id=user.id,
        kind="embed",
        units=max(1, doc.chunk_count),
        meta={"action": "knowledge.faq", "chunks": doc.chunk_count},
    )
    audit.log_activity(
        db,
        organization_id=organization.id,
        user_id=user.id,
        action="knowledge.faq_created",
        entity_type="knowledge_document",
        entity_id=doc.id,
    )
    db.commit()
    db.refresh(doc)
    return _doc_out(doc)


@router.get("/tags", response_model=list[TagOut])
def list_tags(
    slug: str,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> list[TagOut]:
    rows = db.execute(
        select(KnowledgeTag.name, func.count(document_tags.c.document_id))
        .outerjoin(document_tags, document_tags.c.tag_id == KnowledgeTag.id)
        .where(KnowledgeTag.organization_id == membership.organization_id)
        .group_by(KnowledgeTag.name)
        .order_by(KnowledgeTag.name)
    ).all()
    return [TagOut(name=name, count=count) for name, count in rows]


@router.post("/search", response_model=KnowledgeSearchOut)
def search_knowledge(
    slug: str,
    data: KnowledgeSearchRequest,
    membership: Membership = Depends(get_workspace_membership),
    db: Session = Depends(get_db),
) -> KnowledgeSearchOut:
    organization = db.get(Organization, membership.organization_id)
    plans.check_request_quota(db, organization)
    hits = knowledge_service.search(
        db, organization.id, data.query, top_k=data.top_k
    )
    usage.track(
        db,
        organization_id=organization.id,
        kind="search",
        units=1,
        meta={"action": "knowledge.search", "query": data.query[:120]},
    )
    db.commit()
    return KnowledgeSearchOut(
        query=data.query,
        hits=[KnowledgeHit(**hit) for hit in hits],
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    slug: str,
    document_id: str,
    membership: Membership = Depends(get_workspace_membership),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    doc = knowledge_service.delete_document(db, membership.organization_id, document_id)
    audit.log_activity(
        db,
        organization_id=membership.organization_id,
        user_id=user.id,
        action="knowledge.deleted",
        entity_type="knowledge_document",
        entity_id=doc.id,
        metadata={"filename": doc.filename},
    )
    db.commit()
