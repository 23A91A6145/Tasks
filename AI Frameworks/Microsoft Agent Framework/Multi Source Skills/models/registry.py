from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ConflictDetail(BaseModel):
    skill_name: str
    sources: List[Dict[str, Any]] = Field(
        ..., 
        description="List of details for each conflicting skill instance, including source_type, source_path, and priority"
    )
    winning_source_type: str
    winning_source_path: str
    winning_priority: int
    resolution_reason: str

class RegistrySummary(BaseModel):
    total_loaded_skills: int
    active_skills: List[str]
    conflicts_detected: int
    conflicts: List[ConflictDetail] = Field(default_factory=list)
    load_time_seconds: float
