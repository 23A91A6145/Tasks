import time
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class BenchmarkMetric(BaseModel):
    prompt: str
    category: str
    provider: str
    model: str
    latency: float = 0.0
    ttft: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    tps: float = 0.0
    quality_score: float = 0.0
    response_text: str = ""
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    cost: float = 0.0
    ram_used_gb: float = 0.0
    ram_delta_gb: float = 0.0

    class Config:
        arbitrary_types_allowed = True
