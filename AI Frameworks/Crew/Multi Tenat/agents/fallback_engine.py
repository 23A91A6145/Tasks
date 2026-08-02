"""Zero-cost rule-based AI engine.

Works fully offline: classifies tickets with keyword rules, retrieves the
most relevant knowledge chunks and assembles a grounded reply. Used when
no LLM API key is configured, and as a safety net in every engine.
"""

import re
from dataclasses import replace

from sqlalchemy.orm import Session

from ..models import Organization
from ..services import knowledge_service
from ..services.embeddings import get_embedder
from ..services.vector import get_vector_store
from .engine import HandleResult

CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("billing", ["refund", "charge", "bill", "invoice", "payment", "pricing", "plan", "card", "receipt", "money"]),
    ("account", ["login", "password", "sign in", "sign-in", "account", "locked", "2fa", "two-factor", "verification", "otp", "access"]),
    ("technical", ["error", "crash", "bug", "install", "connect", "not working", "failed", "timeout", "config", "setup", "permission", "blank", "freeze"]),
    ("order", ["order", "shipping", "delivery", "tracking", "return", "cancel order", "shipment"]),
    ("security", ["breach", "hacked", "compromised", "unauthorized", "suspicious", "fraud", "data leak"]),
]

URGENT_RULES = [
    "urgent", "emergency", "critical", "down", "outage", "breach", "security",
    "asap", "immediately", "tonight", "deadline", "lost", "hacked", "data leak",
]

HIGH_RULES = ["billing", "refund", "charge", "invoice", "payment", "fraud", "legal", "compliance"]


def classify(subject: str, body: str) -> tuple[str, list[str]]:
    text = f"{subject} {body}".lower()
    for category, keywords in CATEGORY_RULES:
        if any(keyword in text for keyword in keywords):
            return category, keywords
    return "general", []


def detect_priority(subject: str, body: str, classification: str) -> str:
    text = f"{subject} {body}".lower()
    if any(word in text for word in URGENT_RULES):
        return "urgent"
    if classification in ("billing", "security") or any(word in text for word in HIGH_RULES):
        return "high"
    return "medium"


def _retrieve(db: Session, organization_id: str, query: str, top_k: int = 4) -> list[dict]:
    return knowledge_service.search(db, organization_id, query, top_k=top_k)


def handle_ticket(
    db: Session,
    organization: Organization,
    subject: str,
    body: str,
    top_k: int = 4,
) -> HandleResult:
    classification, keywords = classify(subject, body)
    priority = detect_priority(subject, body, classification)
    hits = _retrieve(db, organization.id, f"{subject} {body}", top_k=top_k)

    best_score = hits[0]["score"] if hits else 0.0
    urgent = priority == "urgent"
    low_confidence = best_score < 0.15 or not hits
    escalate = urgent or low_confidence

    if hits:
        draft = (
            f"Hi, thanks for reaching out. I found this in your workspace's knowledge base "
            f"which should help:\n\n"
            + "\n\n".join(f"• {hit['text']}" for hit in hits[:2])
            + "\n\nIf this doesn't fully resolve your issue, let me know and I'll loop in a teammate."
        )
    else:
        draft = (
            "Hi, thanks for contacting us. I couldn't find a direct answer in our knowledge "
            "base yet, so I've flagged this for a teammate to review and I'll follow up shortly. "
            "Could you share a couple more details (steps you took, error messages, account type)?"
        )

    summary = (
        f"Classified as {classification} ({priority} priority). "
        f"{len(hits)} knowledge source(s) matched; "
        + ("flagged for human review." if escalate else "draft response ready from knowledge base.")
    )

    return HandleResult(
        classification=classification,
        priority=priority,
        draft=draft,
        summary=summary,
        sources=[
            {"text": hit["text"], "score": hit["score"], "filename": hit["filename"]}
            for hit in hits
        ],
        escalate=escalate,
        confidence=round(best_score, 4) if hits else 0.0,
        engine="fallback",
        notes=f"Matched keywords: {', '.join(keywords) if keywords else 'none'}",
    )
