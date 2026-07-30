import os
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError
import json


class ProviderConfig:
    def __init__(self, name: str, display: str, env_key: str, env_url: str = ""):
        self.name = name
        self.display = display
        self.env_key = env_key
        self.env_url = env_url

    @property
    def api_key(self) -> str:
        return os.getenv(self.env_key, "")

    @property
    def base_url(self) -> str:
        return os.getenv(self.env_url, "") if self.env_url else ""

    @property
    def is_configured(self) -> bool:
        if self.name == "ollama":
            return True
        return bool(self.api_key)

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "display": self.display,
            "configured": self.is_configured,
        }


_PROVIDERS: Dict[str, ProviderConfig] = {
    "ollama": ProviderConfig("ollama", "Ollama (Free)", "", ""),
    "openai": ProviderConfig("openai", "OpenAI", "OPENAI_API_KEY"),
    "openrouter": ProviderConfig("openrouter", "OpenRouter (Free Tier)", "OPENROUTER_API_KEY", "OPENROUTER_BASE_URL"),
}


def get_providers() -> Dict[str, ProviderConfig]:
    return _PROVIDERS


def get_available_providers() -> List[Dict]:
    result = []
    for name, cfg in _PROVIDERS.items():
        if name == "ollama":
            try:
                req = Request("http://localhost:11434/api/tags", method="GET")
                with urlopen(req, timeout=2) as resp:
                    if resp.status == 200:
                        result.append(cfg.to_dict())
                        continue
            except (URLError, OSError):
                pass
            result.append({**cfg.to_dict(), "configured": False})
        else:
            result.append(cfg.to_dict())
    return result


def set_active_provider(provider_name: str) -> bool:
    if provider_name not in _PROVIDERS:
        return False
    cfg = _PROVIDERS[provider_name]
    if provider_name == "ollama":
        return True
    return cfg.is_configured
