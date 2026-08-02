"""Outbound webhooks — notify external systems when workspace events happen.

Tenants configure a ``webhook_url`` (and optional ``webhook_secret``) in workspace
settings. When events fire (ticket created, AI handled, flow approved) we POST a
JSON payload signed with HMAC-SHA256 to that URL. This is how you integrate
TenantDesk AI with Slack, Zapier, your CRM, or any HTTP endpoint.
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from sqlalchemy.orm import Session

from ..models import Organization

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 8


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None


def get_config(org: Organization) -> dict:
    settings = org.settings or {}
    return {
        "webhook_url": settings.get("webhook_url", ""),
        "webhook_secret": settings.get("webhook_secret", ""),
        "webhook_events": list(settings.get("webhook_events", ["ticket.created", "ticket.ai_handled", "flow.approved"])),
    }


def set_config(
    db: Session,
    org: Organization,
    *,
    url: str,
    secret: str = "",
    events: list[str] | None = None,
) -> dict:
    settings = dict(org.settings or {})
    settings["webhook_url"] = url.strip()
    settings["webhook_secret"] = secret.strip()
    if events is not None:
        settings["webhook_events"] = [e for e in events if e]
    org.settings = settings
    db.commit()
    db.refresh(org)
    return get_config(org)


def _sign(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def deliver(org: Organization, event: str, data: dict) -> dict:
    """Deliver one event to the tenant's webhook URL. Never raises — callers log/return."""
    cfg = get_config(org)
    url = cfg["webhook_url"]
    if not url:
        return {"delivered": False, "error": "no webhook configured", "event": event}

    payload = {
        "event": event,
        "workspace_slug": org.slug,
        "workspace_name": org.name,
        "sent_at": _iso(datetime.now(timezone.utc)),
        "data": data,
    }
    body = json.dumps(payload, default=str).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if cfg.get("webhook_secret"):
        headers["X-Webhook-Signature"] = "sha256=" + _sign(body, cfg["webhook_secret"])
    headers["X-Webhook-Event"] = event

    try:
        req = Request(url, data=body, headers=headers, method="POST")
        with urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            return {"delivered": True, "status": resp.status, "event": event}
    except Exception as exc:  # noqa: BLE001 — webhook delivery must never crash the API
        logger.warning("webhook %s → %s failed: %s", event, url, exc)
        return {"delivered": False, "error": str(exc)[:200], "event": event}
