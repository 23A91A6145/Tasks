"""Outbound notifications (email). ``EMAIL_MODE=log`` is the free, offline
default: reset links are printed to the server log and returned to the UI so
the flow works end-to-end on a laptop with zero SMTP configuration.
``EMAIL_MODE=smtp`` switches to real delivery via SMTP settings.
"""

import logging

from ..core.config import settings

logger = logging.getLogger("tenantdesk.email")

PASSWORD_RESET_PATH = "/reset-password?token="


def _reset_url(token: str) -> str:
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}{PASSWORD_RESET_PATH}{token}"


def send_password_reset(user_email: str, token: str) -> str | None:
    """Send a password reset email. Returns the reset URL when it is safe to
    show it to the requester (dev mode only), otherwise None."""
    url = _reset_url(token)
    if settings.EMAIL_MODE.lower() != "smtp":
        logger.warning(
            "PASSWORD RESET requested for %s → %s  (EMAIL_MODE=log — no email sent)",
            user_email,
            url,
        )
        return url
    if not settings.SMTP_HOST:
        logger.warning("EMAIL_MODE=smtp but SMTP_HOST is empty — falling back to log mode")
        return url
    try:
        import smtplib
        from email.mime.text import MIMEText

        subject = "Reset your TenantDesk AI password"
        body = (
            "Someone requested a password reset for your TenantDesk AI account.\n\n"
            f"Reset link (valid 15 minutes):\n{url}\n\n"
            "If this wasn't you, you can safely ignore this email.\n"
        )
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = user_email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [user_email], msg.as_string())
        return None
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to send password reset email to %s: %s", user_email, exc)
        return url
