from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FlowRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    flow_key: str
    status: str
    current_step: str
    input_data: dict = {}
    checkpoint: dict = {}
    output_data: dict = {}
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FlowResumeRequest(BaseModel):
    approved: bool


class FlowTriggerRequest(BaseModel):
    flow_key: str = Field(pattern=r"^(escalation|feedback)$")
    ticket_id: str = Field(min_length=1)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=2000)
    reason: Optional[str] = Field(default=None, max_length=1000)
