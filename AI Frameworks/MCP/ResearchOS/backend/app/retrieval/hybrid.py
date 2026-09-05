from typing import List, Dict
from backend.app.models.schemas import EvidenceChunk
from backend.app.retrieval.keyword import BM25Retriever
from backend.app.retrieval.semantic import SemanticRetriever

class HybridRRFRetriever:
    """
    Reciprocal Rank Fusion (RRF) Hybrid Retriever.
    RRF Score = 1 / (K + Rank_dense) + 1 / (K + Rank_sparse)
    """
    def __init__(self, k: int = 60):
        self.k = k
        self.bm25 = BM25Retriever()
        self.semantic = SemanticRetriever()

    def search(self, query: str, chunks: List[EvidenceChunk], top_k: int = 5) -> List[EvidenceChunk]:
        if not chunks:
            return []
        if len(chunks) <= top_k:
            return chunks

        # Index and search BM25
        self.bm25.index(chunks)
        sparse_res = self.bm25.search(query, top_k=len(chunks))

        # Semantic Search
        dense_res = self.semantic.search(query, chunks, top_k=len(chunks))

        # RRF Aggregation
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, EvidenceChunk] = {c.id: c for c in chunks}

        for rank, (chunk, _) in enumerate(sparse_res, start=1):
            rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0.0) + (1.0 / (self.k + rank))

        for rank, (chunk, _) in enumerate(dense_res, start=1):
            rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0.0) + (1.0 / (self.k + rank))

        sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        top_chunks = []
        for chunk_id, score in sorted_chunks[:top_k]:
            c = chunk_map[chunk_id]
            c.score = float(score)
            top_chunks.append(c)

        return top_chunks
