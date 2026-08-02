from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    subject: str = Field(min_length=2, max_length=255)
    body: str = Field(min_length=2, max_length=20_000)
    priority: str = Field(default="medium", pattern=r"^(low|medium|high|urgent)$")


class TicketMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ticket_id: str
    sender: str
    sender_user_id: Optional[str] = None
    sender_name: Optional[str] = None
    content: str
    meta_json: dict = {}
    created_at: datetime


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    subject: str
    body: str
    status: str
    priority: str
    classification: Optional[str] = None
    ai_summary: Optional[str] = None
    created_by_id: Optional[str] = None
    created_by_name: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class TicketDetailOut(TicketOut):
    messages: list[TicketMessageOut] = []


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)


class TicketHandleOut(BaseModel):
    ticket: TicketDetailOut
    flow_run: Optional[dict] = None
    draft: str = ""
    classification: str = "general"
    priority: str = "medium"
    escalate: bool = False
    engine: str = "fallback"
    sources: list[dict] = []
    awaiting_approval: bool = False
