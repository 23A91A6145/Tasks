"""LLM providers.

One OpenAI-compatible client covers OpenAI, Groq, OpenRouter, Gemini and
Ollama (all have `/v1/chat/completions`). A fallback provider returns
deterministic canned replies so the whole platform still works offline
with zero API keys (demo / CI / development).
"""

from dataclasses import dataclass, field
from typing import Optional

from ..core.config import settings

try:  # optional dependency
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass
class LLMResult:
    text: str
    usage: LLMUsage = field(default_factory=LLMUsage)


PROVIDER_DEFAULTS: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "ollama": "http://localhost:11434/v1",
}


class LLMProvider:
    name: str = "base"
    configured: bool = False

    def complete(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> LLMResult:
        raise NotImplementedError


class OpenAICompatLLM(LLMProvider):
    """Any OpenAI-compatible chat-completions endpoint."""

    name = "openai-compatible"

    def __init__(self, base_url: str, api_key: str, model: str):
        self.model = model
        self.configured = bool(api_key) or "localhost" in base_url
        if OpenAI is None:
            self.configured = False
            self._client = None
        else:
            self._client = OpenAI(base_url=base_url or None, api_key=api_key or "not-needed")

    def complete(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> LLMResult:
        if self._client is None:
            return LLMResult(text="", usage=LLMUsage())
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            usage = getattr(resp, "usage", None)
            return LLMResult(
                text=resp.choices[0].message.content or "",
                usage=LLMUsage(
                    prompt_tokens=getattr(usage, "prompt_tokens", 0),
                    completion_tokens=getattr(usage, "completion_tokens", 0),
                ),
            )
        except Exception as exc:  # network / auth errors → surface, caller decides
            raise RuntimeError(f"LLM request failed: {exc}") from exc


class FallbackLLM(LLMProvider):
    """Zero-cost deterministic provider used when no API key is configured."""

    name = "fallback"

    def __init__(self) -> None:
        self.configured = False

    def complete(
        self,
        system: str,
        user: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> LLMResult:
        return LLMResult(
            text=(
                "I’m operating in offline demo mode (no LLM API key configured). "
                "The following answer was assembled from your knowledge base."
            )
        )


def llm_base_url() -> str:
    if settings.LLM_BASE_URL:
        return settings.LLM_BASE_URL
    return PROVIDER_DEFAULTS.get(settings.LLM_PROVIDER, PROVIDER_DEFAULTS["openai"])


def get_llm() -> LLMProvider:
    """Return the best available LLM provider based on configuration."""
    if settings.LLM_API_KEY or "localhost" in llm_base_url():
        return OpenAICompatLLM(llm_base_url(), settings.LLM_API_KEY, settings.LLM_MODEL)
    return FallbackLLM()


def crew_llm_kwargs() -> Optional[dict]:
    """Build kwargs for a CrewAI LLM, or None if no provider is configured."""
    if not (settings.LLM_API_KEY or "localhost" in llm_base_url()):
        return None
    model = settings.LLM_MODEL
    if settings.LLM_PROVIDER not in ("openai", "custom"):
        model = f"{settings.LLM_PROVIDER}/{model}"
    else:
        model = f"openai/{model}"
    kwargs: dict = {
        "model": model,
        "base_url": llm_base_url() or None,
        "api_key": settings.LLM_API_KEY or "not-needed",
    }
    return kwargs
