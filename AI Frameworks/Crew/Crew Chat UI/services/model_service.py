import os
import json
from urllib.request import urlopen, Request
from urllib.error import URLError
from typing import List, Dict


class ModelService:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url

    def list_ollama_models(self) -> List[Dict]:
        try:
            req = Request(f"{self.ollama_url}/api/tags", method="GET", headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                models = []
                for m in data.get("models", []):
                    name = m["name"]
                    families = m.get("details", {}).get("families", [])
                    models.append({
                        "name": name,
                        "size": m.get("size", 0),
                        "family": families[0] if families else "unknown",
                    })
                return sorted(models, key=lambda x: x["name"])
        except (URLError, OSError, json.JSONDecodeError):
            return []

    def get_chat_models(self) -> List[str]:
        models = self.list_ollama_models()
        chat_models = []
        for m in models:
            name = m["name"]
            if "embed" not in name.lower():
                chat_models.append(name)
        return chat_models

    def get_recommended_model(self) -> str:
        models = self.get_chat_models()
        if not models:
            return "llama3.2:3b"
        priority = ["llama3.2", "llama3", "qwen2.5", "mistral", "phi"]
        for prefix in priority:
            for m in models:
                if m.startswith(prefix):
                    return m
        return models[0]

    def is_model_available(self, model_name: str) -> bool:
        return model_name in self.get_chat_models()

    def pull_model(self, model_name: str) -> bool:
        try:
            import requests
            r = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=5,
            )
            return r.status_code == 200
        except Exception:
            return False
