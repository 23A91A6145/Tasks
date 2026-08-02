from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentConfigOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    key: str
    name: str
    role_description: Optional[str] = None
    llm_model: Optional[str] = None
    enabled: bool
    config: dict = {}
    updated_at: datetime


class AgentConfigUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=80)
    role_description: Optional[str] = Field(default=None, max_length=2000)
    llm_model: Optional[str] = Field(default=None, max_length=120)
    enabled: Optional[bool] = None
