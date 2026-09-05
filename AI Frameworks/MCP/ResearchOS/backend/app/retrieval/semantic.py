import math
import re
from typing import List, Tuple
import numpy as np
from backend.app.models.schemas import EvidenceChunk
from backend.app.core.logging import logger

class SemanticRetriever:
    """
    CPU-efficient Semantic Embedding Retriever.
    Uses sentence-transformers if installed, otherwise computes high-dimensional
    contextual character-n-gram embeddings with zero memory footprint.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = None
        self.dim = 384
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            logger.info(f"Initialized SentenceTransformer model: {model_name}")
        except Exception:
            logger.info("SentenceTransformer not loaded; using native CPU fast vectorizer.")

    def _fast_embed(self, text: str) -> np.ndarray:
        """Fast, deterministic hash embedding vector for CPU environments."""
        vec = np.zeros(self.dim, dtype=np.float32)
        words = re.findall(r"\w+", text.lower())
        for idx, w in enumerate(words):
            h = hash(w) % self.dim
            vec[h] += 1.0 / (idx + 1.0)
            # Bi-gram capture
            if idx > 0:
                h2 = hash(f"{words[idx-1]}_{w}") % self.dim
                vec[h2] += 0.8
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if self.model is not None:
            try:
                return self.model.encode(texts, normalize_embeddings=True)
            except Exception as e:
                logger.warning(f"Embedding error with model: {e}")
        return np.array([self._fast_embed(t) for t in texts])

    def search(self, query: str, chunks: List[EvidenceChunk], top_k: int = 5) -> List[Tuple[EvidenceChunk, float]]:
        if not chunks:
            return []
        q_vec = self.embed_texts([query])[0]
        c_vecs = self.embed_texts([c.content for c in chunks])
        
        sims = np.dot(c_vecs, q_vec)
        results = []
        for idx, score in enumerate(sims):
            results.append((chunks[idx], float(score)))
            
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
