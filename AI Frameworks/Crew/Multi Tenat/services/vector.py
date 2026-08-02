"""Vector stores for tenant-isolated knowledge.

- ``NumpyVectorStore`` — pure-Python cosine store persisted as JSON per
  tenant namespace. Zero extra services, free, laptop-safe.
- ``QdrantVectorStore`` — Qdrant (embedded local path or remote server).
  One collection per tenant keeps knowledge fully isolated.
"""

import json
import math
import os
import threading
from dataclasses import asdict, dataclass, field
from typing import Optional

from ..core.config import settings


@dataclass
class VectorPoint:
    id: str
    document_id: str
    chunk_index: int
    text: str
    vector: list[float]
    metadata: dict = field(default_factory=dict)


@dataclass
class SearchHit:
    id: str
    document_id: str
    chunk_index: int
    text: str
    score: float
    metadata: dict = field(default_factory=dict)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class NumpyVectorStore:
    """File-backed cosine vector store with a per-namespace JSON document."""

    name = "numpy"

    def __init__(self, root: Optional[str] = None):
        self.root = root or os.path.join(settings.STORAGE_DIR, "vectors")
        os.makedirs(self.root, exist_ok=True)
        self._lock = threading.RLock()

    def _path(self, namespace: str) -> str:
        return os.path.join(self.root, f"{namespace}.json")

    def _load(self, namespace: str) -> list[dict]:
        path = self._path(namespace)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save(self, namespace: str, points: list[dict]) -> None:
        path = self._path(namespace)
        tmp = f"{path}.tmp"
        with open(tmp, "w", encoding="utf-8") as handle:
            json.dump(points, handle)
        os.replace(tmp, path)

    def upsert(self, namespace: str, points: list[VectorPoint]) -> None:
        if not points:
            return
        with self._lock:
            current = self._load(namespace)
            existing = {point["id"]: point for point in current}
            for point in points:
                existing[point.id] = asdict(point)
            self._save(namespace, list(existing.values()))

    def search(self, namespace: str, vector: list[float], top_k: int) -> list[SearchHit]:
        with self._lock:
            points = self._load(namespace)
        scored = [
            (point, _cosine(vector, point["vector"])) for point in points
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [
            SearchHit(
                id=point["id"],
                document_id=point["document_id"],
                chunk_index=point["chunk_index"],
                text=point["text"],
                score=round(score, 4),
                metadata=point.get("metadata", {}),
            )
            for point, score in scored[:top_k]
        ]

    def delete_document(self, namespace: str, document_id: str) -> int:
        with self._lock:
            points = self._load(namespace)
            before = len(points)
            remaining = [p for p in points if p["document_id"] != document_id]
            self._save(namespace, remaining)
            return before - len(remaining)

    def delete_namespace(self, namespace: str) -> int:
        """Drop every vector for a tenant namespace (used when a workspace is deleted)."""
        with self._lock:
            path = self._path(namespace)
            if not os.path.exists(path):
                return 0
            removed = len(self._load(namespace))
            os.remove(path)
            return removed

    def count(self, namespace: str) -> int:
        return len(self._load(namespace))


class QdrantVectorStore:
    """Qdrant-backed store. One collection per tenant namespace."""

    name = "qdrant"

    def __init__(self, url: str, api_key: Optional[str] = None):
        from qdrant_client import QdrantClient

        if url.startswith("./") or url.startswith("/") or url == "local":
            self._client = QdrantClient(path=url if url != "local" else os.path.join(settings.STORAGE_DIR, "qdrant"))
        else:
            self._client = QdrantClient(url=url, api_key=api_key)
        self._collections: set[str] = set()

    def _collection(self, namespace: str) -> str:
        return f"ws_{namespace}"

    def _ensure(self, namespace: str, dim: int) -> None:
        name = self._collection(namespace)
        if name in self._collections:
            return
        from qdrant_client.models import Distance, VectorParams

        if not self._client.collection_exists(name):
            self._client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
        self._collections.add(name)

    def upsert(self, namespace: str, points: list[VectorPoint]) -> None:
        if not points:
            return
        from qdrant_client.models import PointStruct

        dim = len(points[0].vector)
        self._ensure(namespace, dim)
        self._client.upsert(
            collection_name=self._collection(namespace),
            points=[
                PointStruct(
                    id=point.id,
                    vector=point.vector,
                    payload={
                        "document_id": point.document_id,
                        "chunk_index": point.chunk_index,
                        "text": point.text,
                        **point.metadata,
                    },
                )
                for point in points
            ],
        )

    def search(self, namespace: str, vector: list[float], top_k: int) -> list[SearchHit]:
        self._ensure(namespace, len(vector))
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        results = self._client.search(
            collection_name=self._collection(namespace),
            query_vector=vector,
            limit=top_k,
        )
        return [
            SearchHit(
                id=str(point.id),
                document_id=point.payload.get("document_id", ""),
                chunk_index=int(point.payload.get("chunk_index", 0)),
                text=point.payload.get("text", ""),
                score=round(point.score, 4),
                metadata={
                    k: v for k, v in point.payload.items()
                    if k not in ("document_id", "chunk_index", "text")
                },
            )
            for point in results
        ]

    def delete_document(self, namespace: str, document_id: str) -> int:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        hits = self._client.count(
            collection_name=self._collection(namespace),
            count_filter=Filter(
                must=[
                    FieldCondition(key="document_id", match=MatchValue(value=document_id))
                ]
            ),
            exact=True,
        )
        self._client.delete(
            collection_name=self._collection(namespace),
            points_selector=Filter(
                must=[
                    FieldCondition(key="document_id", match=MatchValue(value=document_id))
                ]
            ),
        )
        return hits.count

    def delete_namespace(self, namespace: str) -> int:
        """Drop the whole tenant collection (used when a workspace is deleted)."""
        name = self._collection(namespace)
        if name in self._collections:
            self._collections.remove(name)
        if self._client.collection_exists(name):
            self._client.delete_collection(name)
        return 0

    def count(self, namespace: str) -> int:
        self._ensure(namespace, settings.EMBEDDINGS_DIM)
        return self._client.count(collection_name=self._collection(namespace), exact=True).count


_store_singleton = None
_store_lock = threading.Lock()


def get_vector_store():
    global _store_singleton
    with _store_lock:
        if _store_singleton is None:
            if settings.VECTOR_STORE == "qdrant":
                _store_singleton = QdrantVectorStore(
                    settings.QDRANT_URL or os.path.join(settings.STORAGE_DIR, "qdrant")
                )
            else:
                _store_singleton = NumpyVectorStore()
        return _store_singleton


def reset_vector_store() -> None:
    """Clear the cached store (used by tests)."""
    global _store_singleton
    with _store_lock:
        _store_singleton = None
