import base64 as b64
import hashlib
import secrets
import string

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class HashStringInput(BaseModel):
    value: str = Field(description="String to hash")
    algorithm: str = Field(default="sha256", description="Hash algorithm: md5, sha1, sha256, sha512")


@tool(args_schema=HashStringInput)
def hash_string(value: str, algorithm: str = "sha256") -> str:
    """Hash a string using the specified algorithm.

    Args:
        value: Input string.
        algorithm: md5, sha1, sha256, or sha512.

    Returns:
        Hexadecimal hash digest.
    """
    allowed = {"md5", "sha1", "sha256", "sha512"}
    if algorithm not in allowed:
        return f"Error: unknown algorithm '{algorithm}'. Use: {', '.join(sorted(allowed))}"
    try:
        h = hashlib.new(algorithm, value.encode("utf-8"))
        return h.hexdigest()
    except Exception as e:
        return f"Error hashing: {e}"


class Base64EncodeInput(BaseModel):
    value: str = Field(description="String to encode")


@tool(args_schema=Base64EncodeInput)
def base64_encode(value: str) -> str:
    """Encode a string to base64.

    Args:
        value: Input string.

    Returns:
        Base64-encoded string.
    """
    try:
        encoded = b64.b64encode(value.encode("utf-8")).decode("utf-8")
        return encoded
    except Exception as e:
        return f"Error encoding: {e}"


class Base64DecodeInput(BaseModel):
    value: str = Field(description="Base64 string to decode")


@tool(args_schema=Base64DecodeInput)
def base64_decode(value: str) -> str:
    """Decode a base64 string.

    Args:
        value: Base64-encoded string.

    Returns:
        Decoded string.
    """
    try:
        decoded = b64.b64decode(value.encode("utf-8")).decode("utf-8")
        return decoded
    except Exception as e:
        return f"Error decoding: {e}"


class RandomPasswordInput(BaseModel):
    length: int = Field(default=16, ge=4, le=128, description="Password length")
    special_chars: bool = Field(default=True, description="Include special characters")


@tool(args_schema=RandomPasswordInput)
def random_password(length: int = 16, special_chars: bool = True) -> str:
    """Generate a cryptographically secure random password.

    Args:
        length: Password length.
        special_chars: Whether to include !@#$%^&* etc.

    Returns:
        Random password string.
    """
    chars = string.ascii_letters + string.digits
    if special_chars:
        chars += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    password = "".join(secrets.choice(chars) for _ in range(length))
    return password
