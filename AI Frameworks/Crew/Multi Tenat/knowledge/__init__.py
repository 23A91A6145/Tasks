import sys
from pathlib import Path

# Bridge to apps/backend knowledge pipeline (apps/backend/app/services/knowledge_service.py)
backend_dir = Path(__file__).resolve().parent.parent / "apps" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.services.knowledge_service import (
    ingest_text,
    ingest_file,
    ingest_url,
    ingest_faq,
    search,
    delete_document,
    list_tags,
    chunk_text,
    extract_text,
    extract_url,
    load_persisted_text,
)

__all__ = [
    "ingest_text",
    "ingest_file",
    "ingest_url",
    "ingest_faq",
    "search",
    "delete_document",
    "list_tags",
    "chunk_text",
    "extract_text",
    "extract_url",
    "load_persisted_text",
]
