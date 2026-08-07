import re
from typing import Dict, Any

# Simple regex-based PII patterns
SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
CREDIT_CARD_REGEX = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')

class PIIShield:
    @staticmethod
    def redact(text: str) -> str:
        if not text:
            return ""
        
        redacted = text
        
        # Redact SSNs
        redacted = SSN_REGEX.sub("[REDACTED_SSN]", redacted)
        
        # Redact Credit Cards
        redacted = CREDIT_CARD_REGEX.sub("[REDACTED_CARD]", redacted)
        
        # Redact Emails
        redacted = EMAIL_REGEX.sub("[REDACTED_EMAIL]", redacted)
        
        # Redact Phones
        redacted = PHONE_REGEX.sub("[REDACTED_PHONE]", redacted)
        
        return redacted

    @staticmethod
    def contains_pii(text: str) -> bool:
        if not text:
            return False
        return bool(
            SSN_REGEX.search(text) or 
            CREDIT_CARD_REGEX.search(text) or 
            EMAIL_REGEX.search(text) or 
            PHONE_REGEX.search(text)
        )
