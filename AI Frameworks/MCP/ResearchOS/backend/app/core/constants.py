from enum import Enum

class ResearchMode(str, Enum):
    QUICK = "quick"
    DEEP = "deep"
    ACADEMIC = "academic"
    TECH_COMPARISON = "tech_comparison"
    COMPETITIVE = "competitive"

class RunStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    SEARCHING = "searching"
    EXTRACTING = "extracting"
    VERIFYING = "verifying"
    SYNTHESIZING = "synthesizing"
    CRITIQUING = "critiquing"
    COMPLETED = "completed"
    FAILED = "failed"

class SourceType(str, Enum):
    ACADEMIC = "academic"
    WEB = "web"
    DOCUMENTATION = "documentation"
    USER_DOC = "user_doc"

class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PARTIALLY_SUPPORTED = "partially_supported"
    CONTESTED = "contested"
    UNSUPPORTED = "unsupported"

# Guardrail & Resource Limits (Ubuntu 16GB RAM / Free-Tier Friendly)
MAX_STEPS_DEFAULT = 25
MAX_SEARCHES_DEFAULT = 12
MAX_SOURCES_DEFAULT = 30
MAX_RUNTIME_SECONDS_DEFAULT = 300
DEFAULT_CONFIDENCE_THRESHOLD = 0.75
DEFAULT_RRF_K = 60
