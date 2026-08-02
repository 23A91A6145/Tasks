"""AI engine facade — pick and run the best engine for ticket handling."""

from sqlalchemy.orm import Session

from ..models import Organization
from .engine import HandleResult, resolve_engine_name


def handle_ticket(
    db: Session,
    organization: Organization,
    subject: str,
    body: str,
    top_k: int = 4,
) -> HandleResult:
    engine = resolve_engine_name()

    if engine == "crewai":
        from . import crew_support

        result = crew_support.handle_ticket(db, organization, subject, body, top_k=top_k)
    elif engine == "llm":
        from . import direct_engine

        result = direct_engine.handle_ticket(db, organization, subject, body, top_k=top_k)
    else:
        from . import fallback_engine

        result = fallback_engine.handle_ticket(db, organization, subject, body, top_k=top_k)
        if result.engine == "fallback" and result.notes is None:
            result.notes = ""

    return result
