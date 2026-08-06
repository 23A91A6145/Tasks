from pydantic import BaseModel, Field
from typing import List, Optional

class ProviderMetadata(BaseModel):
    name: str = Field(..., description="Unique name of the provider")
    priority: int = Field(0, description="Default priority level for skills retrieved from this provider")
    description: Optional[str] = Field(None, description="Optional description of the provider")
    enabled: bool = Field(True, description="Whether this provider is active and enabled")
