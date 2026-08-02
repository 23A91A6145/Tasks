"""AI engine selection and shared result types.

Three engines power ticket handling, chosen automatically:

1. ``crewai``   — full CrewAI hierarchical crew (Manager → Router / Knowledge /
                 Support / Escalation / Report). Requires Python ≤3.13 + LLM key.
2. ``llm``      — direct LLM calls with RAG context (no CrewAI needed).
3. ``fallback`` — zero-cost rule engine over the tenant knowledge base.
"""

from dataclasses import dataclass, field

from ..core.config import settings


@dataclass
class HandleResult:
    classification: str = "general"
    priority: str = "medium"
    draft: str = ""
    summary: str = ""
    sources: list[dict] = field(default_factory=list)
    escalate: bool = False
    confidence: float = 0.5
    engine: str = "fallback"
    notes: str = ""


def is_crewai_available() -> bool:
    try:
        import crewai  # noqa: F401

        return True
    except ImportError:
        return False


def is_llm_configured() -> bool:
    from ..services.llm import get_llm

    return get_llm().configured


def resolve_engine_name() -> str:
    """Decide which engine implementation should run for this deployment."""
    requested = settings.AI_ENGINE
    if requested == "crewai":
        if not is_crewai_available():
            return "fallback"
        return "crewai" if is_llm_configured() else "fallback"
    if requested == "llm":
        return "llm" if is_llm_configured() else "fallback"
    if requested == "fallback":
        return "fallback"
    # auto
    if is_crewai_available() and is_llm_configured():
        return "crewai"
    if is_llm_configured():
        return "llm"
    return "fallback"


def engine_status() -> dict:
    name = resolve_engine_name()
    from ..services.llm import llm_base_url, settings as llm_settings

    return {
        "engine": name,
        "crewai_available": is_crewai_available(),
        "llm_configured": is_llm_configured(),
        "llm_provider": llm_settings.LLM_PROVIDER,
        "llm_model": llm_settings.LLM_MODEL,
        "llm_base_url": llm_base_url(),
        "embeddings_provider": settings.EMBEDDINGS_PROVIDER,
        "vector_store": settings.VECTOR_STORE,
        "notes": (
            "Configure LLM_API_KEY (or run Ollama) for real AI generation. "
            "The fallback engine works fully offline using keyword + RAG matching."
            if name == "fallback"
            else ""
        ),
    }
