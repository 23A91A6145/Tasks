import re
from urllib.parse import urlparse

class SecuritySanitizer:
    """Defends against Indirect Prompt Injection and SSRF attacks."""

    PRIVATE_IP_PATTERNS = [
        r"^127\.",
        r"^10\.",
        r"^172\.(1[6-9]|2[0-9]|3[0-1])\.",
        r"^192\.168\.",
        r"^localhost",
        r"^0\.0\.0\.0"
    ]

    INJECTION_TRIGGERS = [
        r"ignore (all )?previous instructions",
        r"system prompt override",
        r"you are now a",
        r"disregard safety guidelines",
        r"send (api key|password|credentials)",
        r"<script.*?>",
    ]

    @classmethod
    def validate_url_safety(cls, url: str) -> bool:
        """SSRF Prevention: Blocks loopback, private RFC1918 subnets, and malformed protocols."""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ["http", "https"]:
                return False
            hostname = parsed.hostname or ""
            for pattern in cls.PRIVATE_IP_PATTERNS:
                if re.search(pattern, hostname, re.IGNORECASE):
                    return False
            return True
        except Exception:
            return False

    @classmethod
    def sanitize_untrusted_content(cls, raw_content: str) -> str:
        """Wraps untrusted web data in XML delimiters and neutralizes common injection phrases."""
        sanitized = raw_content
        for pattern in cls.INJECTION_TRIGGERS:
            sanitized = re.sub(pattern, "[BLOCKED_INSTRUCTION]", sanitized, flags=re.IGNORECASE)
        # Encapsulate strictly in data boundaries
        return f"<source_data>\n{sanitized.strip()}\n</source_data>"
