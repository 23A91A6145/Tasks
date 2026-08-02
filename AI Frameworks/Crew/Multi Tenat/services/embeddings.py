"""Embedding providers for the RAG pipeline.

- ``hash``   — zero-dependency hashed bag-of-words vectors (free, offline,
              deterministic). Perfect for demos, CI and laptops.
- ``openai`` — any OpenAI-compatible embeddings endpoint (OpenAI, Groq,
              OpenRouter, Gemini, Ollama, Jina).
- ``local``  — sentence-transformers on-device model (optional, heavy).
"""

import hashlib
import math
import re
from typing import Protocol

from ..core.config import settings

TOKEN_RE = re.compile(r"[a-z0-9']+")
_TOKEN_WEIGHT = 5  # boost for exact token matches


class Embedder(Protocol):
    name: str
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


def _l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]


class HashingEmbedder:
    """Deterministic hashed bag-of-words embedding with token hashing and sign."""

    name = "hash"
    dim = settings.EMBEDDINGS_DIM

    def __init__(self, dim: int | None = None):
        if dim:
            self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vec = [0.0] * self.dim
            tokens = TOKEN_RE.findall(text.lower())
            for token in tokens:
                digest = hashlib.sha256(token.encode("utf-8")).digest()
                index = int.from_bytes(digest[:4], "big") % self.dim
                sign = 1.0 if digest[4] % 2 == 0 else -1.0
                vec[index] += sign * _TOKEN_WEIGHT
            vectors.append(_l2_normalize(vec))
        return vectors


class OpenAIEmbedder:
    name = "openai"
    dim = settings.EMBEDDINGS_DIM

    def __init__(self, base_url: str, api_key: str, model: str):
        self.model = model
        try:
            from openai import OpenAI
        except ImportError:  # pragma: no cover
            raise RuntimeError("openai package is not installed")
        self._client = OpenAI(base_url=base_url or None, api_key=api_key or "not-needed")

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        resp = self._client.embeddings.create(model=self.model, input=texts)
        ordered = sorted(resp.data, key=lambda item: item.index)
        return [item.embedding for item in ordered]


class LocalEmbedder:
    """On-device sentence-transformers embeddings (requires torch)."""

    name = "local"
    dim = settings.EMBEDDINGS_DIM

    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = model
        from sentence_transformers import SentenceTransformer  # lazy, heavy

        self._encoder = SentenceTransformer(model)
        self.dim = self._encoder.get_sentence_embedding_dimension()

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [vec.tolist() for vec in self._encoder.encode(texts, normalize_embeddings=True)]


def get_embedder() -> Embedder:
    provider = settings.EMBEDDINGS_PROVIDER
    if provider == "openai":
        base = settings.EMBEDDINGS_BASE_URL or "https://api.openai.com/v1"
        return OpenAIEmbedder(base, settings.EMBEDDINGS_API_KEY, settings.EMBEDDINGS_MODEL)
    if provider == "local":
        return LocalEmbedder()
    return HashingEmbedder()
