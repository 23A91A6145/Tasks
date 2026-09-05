from typing import List
from backend.app.models.schemas import SourceDocument

class EvidenceReranker:
    """Reranks retrieved candidate sources based on authority, recency, and relevance."""
    
    @staticmethod
    def rerank_sources(sources: List[SourceDocument], top_n: int = 15) -> List[SourceDocument]:
        # Deduplicate by URL
        seen_urls = set()
        unique_sources = []
        for s in sources:
            if s.url not in seen_urls:
                seen_urls.add(s.url)
                unique_sources.append(s)

        # Score based on domain credibility and snippet quality
        def score_source(s: SourceDocument) -> float:
            score = s.reliability_score
            # Academic or documentation boost
            if s.source_type.value in ["academic", "documentation"]:
                score += 0.15
            # Recency boost
            if s.published_date and ("2025" in s.published_date or "2026" in s.published_date):
                score += 0.10
            return score

        unique_sources.sort(key=score_source, reverse=True)
        return unique_sources[:top_n]
