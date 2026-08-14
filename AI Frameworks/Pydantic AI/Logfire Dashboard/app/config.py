"""Application configuration and settings."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class AgentConfig(BaseModel):
    """Configuration for the Customer Support Agent and Evaluation Harness."""

    app_name: str = "AgentEval Lab"
    version: str = "0.1.0"
    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )
    model_name: str = Field(
        default_factory=lambda: os.getenv("AGENT_MODEL", "test")
    )
    judge_model_name: str = Field(
        default_factory=lambda: os.getenv("JUDGE_MODEL", "test")
    )
    logfire_token: str | None = Field(
        default_factory=lambda: os.getenv("LOGFIRE_TOKEN")
    )
    logfire_send_to_logfire: bool = Field(
        default_factory=lambda: os.getenv("LOGFIRE_SEND_TO_LOGFIRE", "false").lower() == "true"
    )
    min_pass_rate_threshold: float = 0.85
    max_latency_seconds_threshold: float = 5.0
    strict_tool_validation: bool = True


config = AgentConfig()
