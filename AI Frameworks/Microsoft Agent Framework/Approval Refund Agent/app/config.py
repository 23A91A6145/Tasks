"""
Compatibility module.

Imports are re-exported from `app.settings` so existing modules that use
`from app.config import ...` continue to work unchanged while the actual
configuration logic lives in one auditable place (`app/settings.py`).
"""
from app.settings import settings, BASE_DIR

HOST = settings.host
PORT = settings.port

LOG_DIR = settings.log_dir
CHECKPOINT_DIR = settings.checkpoint_dir
TEMPLATE_DIR = settings.template_dir

AUDIT_LOG_PATH = settings.audit_log_path
APPROVAL_LOG_PATH = settings.approval_log_path
ERROR_LOG_PATH = settings.error_log_path

LLM_PROVIDER = settings.llm_provider
GROQ_API_KEY = settings.groq_api_key
OLLAMA_API_BASE = settings.ollama_api_base
LLM_MODEL = settings.llm_model

MAX_AUTO_APPROVE_AMOUNT = settings.max_auto_approve_amount
MANAGER_LIMIT = settings.manager_limit
MAX_REFUND_CEILING = settings.max_refund_ceiling
APPROVAL_SLA_TIMEOUT_SECONDS = settings.approval_sla_timeout_seconds

RATE_LIMIT_PER_MINUTE = settings.rate_limit_per_minute
SESSION_ID_HEADER = settings.session_id_header
REVIEWER_OVERRIDE_HEADER = settings.reviewer_override_header

SEED_DEMO_DATA = settings.seed_demo_data
