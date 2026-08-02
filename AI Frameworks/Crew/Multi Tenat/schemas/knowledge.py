from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    source_type: str
    file_type: str
    source_url: Optional[str] = None
    size_bytes: int
    status: str
    error: Optional[str] = None
    chunk_count: int
    created_at: datetime
    updated_at: datetime
    tags: list[str] = []


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)


class KnowledgeHit(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    text: str
    score: float
    filename: str = ""
    source_type: str = ""


class KnowledgeSearchOut(BaseModel):
    query: str
    hits: list[KnowledgeHit] = []


class URLIngest(BaseModel):
    url: str = Field(min_length=5, max_length=1000)


class TextIngest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    content: str = Field(min_length=5, max_length=200_000)
    tags: list[str] = Field(default_factory=list, max_length=20)


class FAQIngest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    content: str = Field(min_length=5, max_length=200_000)


class TagOut(BaseModel):
    name: str
    count: int = 0
