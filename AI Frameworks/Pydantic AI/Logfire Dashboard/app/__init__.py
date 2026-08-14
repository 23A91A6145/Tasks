"""AgentEval Lab - Core Application Package."""

from app.agent import create_support_agent, run_support_agent, SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2
from app.config import config, AgentConfig
from app.dependencies import SupportDependencies, create_default_dependencies, CustomerRecord, OrderRecord

__all__ = [
    "create_support_agent",
    "run_support_agent",
    "SYSTEM_PROMPT_V1",
    "SYSTEM_PROMPT_V2",
    "config",
    "AgentConfig",
    "SupportDependencies",
    "create_default_dependencies",
    "CustomerRecord",
    "OrderRecord",
]
