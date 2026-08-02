from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_type: str
    status: str
    label: Optional[str] = None
    current_step: str
    total_steps: int
    progress: int
    input_data: dict = {}
    checkpoint: dict = {}
    result: dict = {}
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class JobCreate(BaseModel):
    job_type: str = Field(pattern=r"^(index_document|crawl_website|batch_faq|weekly_report)$")
    document_id: Optional[str] = None
    url: Optional[str] = Field(default=None, max_length=1000)
    max_pages: Optional[int] = Field(default=10, ge=1, le=50)
    items: Optional[list[dict]] = None
    name: Optional[str] = None
    content: Optional[str] = None
    label: Optional[str] = Field(default=None, max_length=255)
