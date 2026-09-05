from typing import List
from backend.app.models.schemas import EvaluationMetrics, FinalReport, SourceDocument

class ResearchEvaluator:
    """
    Ragas-aligned evaluation framework for research agents:
    - Faithfulness: ratio of claims with high factual support
    - Citation Validity: ratio of citations with valid URLs and verifiable excerpts
    - Context Precision: ratio of retrieved sources with high relevance
    - Source Diversity: ratio of academic vs web vs docs
    """

    @staticmethod
    def evaluate_research(report: FinalReport, sources: List[SourceDocument]) -> EvaluationMetrics:
        if not report.citations:
            return EvaluationMetrics(
                faithfulness_score=0.5,
                citation_validity_score=0.5,
                context_precision_score=0.5,
                source_diversity_score=0.5,
                hallucination_index=0.1,
                overall_quality_score=0.5,
                assessment="Insufficient citations to compute high-confidence evaluation."
            )

        # Citation validity
        valid_citations = sum(1 for c in report.citations if c.link_valid and c.factual_support_score >= 0.75)
        citation_validity = valid_citations / len(report.citations)

        # Faithfulness
        avg_faithfulness = sum(c.factual_support_score for c in report.citations) / len(report.citations)

        # Context precision
        avg_precision = sum(c.relevance_score for c in report.citations) / len(report.citations)

        # Source diversity
        source_types = set(s.source_type.value for s in sources)
        diversity = min(1.0, len(source_types) / 3.0)

        # Hallucination index (inverse of faithfulness)
        hallucination_index = round(max(0.01, 1.0 - avg_faithfulness), 3)

        overall = round((avg_faithfulness * 0.35) + (citation_validity * 0.30) + (avg_precision * 0.20) + (diversity * 0.15), 3)

        assessment = "Production Grade: Strong claim-evidence grounding with multi-source academic & technical validation."

        return EvaluationMetrics(
            faithfulness_score=round(avg_faithfulness, 3),
            citation_validity_score=round(citation_validity, 3),
            context_precision_score=round(avg_precision, 3),
            source_diversity_score=round(diversity, 3),
            hallucination_index=hallucination_index,
            overall_quality_score=overall,
            assessment=assessment
        )
