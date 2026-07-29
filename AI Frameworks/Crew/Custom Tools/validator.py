import re

from langchain_core.tools import tool
from pydantic import BaseModel, Field, field_validator


@tool
def validate_email(*, email: str) -> bool:
    """Check if a string is a valid email address.

    Accepts standard email format: local-part@domain.tld

    Args:
        email: Email string to validate.

    Returns:
        True if valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


@tool
def validate_url(*, url: str) -> bool:
    """Check if a string is a valid URL.

    Accepts http, https, and ftp URLs.

    Args:
        url: URL string to validate.

    Returns:
        True if valid, False otherwise.
    """
    pattern = r"^(https?|ftp)://[^\s/$.?#].[^\s]*$"
    return bool(re.match(pattern, url.strip()))


@tool
def validate_phone(*, phone: str, country: str = "US") -> bool:
    """Check if a string is a valid phone number.

    Args:
        phone: Phone number string to validate.
        country: Country code (US, UK, IN). Affects format validation.

    Returns:
        True if valid, False otherwise.
    """
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    patterns = {
        "US": r"^1?\d{10}$",
        "UK": r"^44?\d{10}$",
        "IN": r"^91?\d{10}$",
    }
    pattern = patterns.get(country, patterns["US"])
    return bool(re.match(pattern, cleaned))


class ValidatorInput(BaseModel):
    value: str = Field(description="The string value to validate")
    validator_type: str = Field(
        default="email",
        description="Type of validation: email, url, phone, alphanumeric, numeric",
    )
    country: str = Field(
        default="US",
        description="Country code for phone validation (US, UK, IN)",
    )

    @field_validator("validator_type")
    @classmethod
    def check_type(cls, v):
        allowed = {"email", "url", "phone", "alphanumeric", "numeric"}
        if v not in allowed:
            raise ValueError(f"validator_type must be one of: {', '.join(sorted(allowed))}")
        return v


@tool(args_schema=ValidatorInput)
def validate_v2(
    value: str,
    validator_type: str = "email",
    country: str = "US",
) -> dict:
    """Validate a string against common formats.

    Uses Pydantic schema with constrained validator_type enum.
    Returns detailed validation result with format information.

    Args:
        value: The string to validate.
        validator_type: Type: email, url, phone, alphanumeric, numeric.
        country: Country for phone validation (US, UK, IN).

    Returns:
        Dict with valid (bool), type (str), and formatted (str).
    """
    if validator_type == "email":
        valid = bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value.strip()))
    elif validator_type == "url":
        valid = bool(re.match(r"^(https?|ftp)://[^\s/$.?#].[^\s]*$", value.strip()))
    elif validator_type == "phone":
        cleaned = re.sub(r"[\s\-\(\)\+]", "", value)
        p = {"US": r"^1?\d{10}$", "UK": r"^44?\d{10}$", "IN": r"^91?\d{10}$"}
        valid = bool(re.match(p.get(country, p["US"]), cleaned))
    elif validator_type == "alphanumeric":
        valid = bool(re.match(r"^[a-zA-Z0-9]+$", value.strip()))
    elif validator_type == "numeric":
        valid = bool(re.match(r"^-?\d+(\.\d+)?$", value.strip()))
    else:
        valid = False

    return {
        "valid": valid,
        "type": validator_type,
        "value": value,
        "formatted": value.strip() if valid else None,
    }
