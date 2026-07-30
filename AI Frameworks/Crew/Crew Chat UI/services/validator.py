import re
from typing import Tuple


class InputValidator:
    MAX_QUERY_LENGTH = 10000
    MIN_QUERY_LENGTH = 1
    MAX_TEMPLATE_LENGTH = 5000

    SANITIZE_PATTERNS = [
        (r"<script[^>]*>.*?</script>", "", re.DOTALL | re.IGNORECASE),
        (r"javascript:", "", re.IGNORECASE),
        (r"on\w+\s*=", "", re.IGNORECASE),
    ]

    @classmethod
    def sanitize(cls, text: str) -> str:
        for pattern, replacement, flags in cls.SANITIZE_PATTERNS:
            text = re.sub(pattern, replacement, text, flags=flags)
        return text.strip()

    @classmethod
    def validate_query(cls, query: str) -> Tuple[bool, str]:
        if not query or not query.strip():
            return False, "Query cannot be empty."
        cleaned = query.strip()
        if len(cleaned) < cls.MIN_QUERY_LENGTH:
            return False, f"Query must be at least {cls.MIN_QUERY_LENGTH} character(s)."
        if len(cleaned) > cls.MAX_QUERY_LENGTH:
            return False, f"Query exceeds {cls.MAX_QUERY_LENGTH:,} character limit ({len(cleaned):,})."
        return True, ""

    @classmethod
    def validate_template(cls, template: str) -> Tuple[bool, str]:
        if not template:
            return False, "Template content cannot be empty."
        if len(template) > cls.MAX_TEMPLATE_LENGTH:
            return False, f"Template exceeds {cls.MAX_TEMPLATE_LENGTH:,} character limit."
        return True, ""

    @classmethod
    def prepare_query(cls, query: str) -> str:
        sanitized = cls.sanitize(query)
        valid, _ = cls.validate_query(sanitized)
        if not valid:
            return ""
        return sanitized
