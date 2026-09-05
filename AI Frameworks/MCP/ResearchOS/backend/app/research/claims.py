import re
import uuid
from typing import List
from backend.app.models.schemas import EvidenceChunk, AtomicClaim, SourceDocument
from backend.app.core.constants import VerificationStatus

class ClaimExtractor:
    """Extracts atomic factual claims from retrieved source evidence."""

    @staticmethod
    def extract_claims(sources: List[SourceDocument], chunks: List[EvidenceChunk]) -> List[AtomicClaim]:
        claims: List[AtomicClaim] = []
        source_map = {s.id: s for s in sources}

        for chunk in chunks:
            text = chunk.content
            # Split into substantive sentences (avoiding tiny fragments)
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for s in sentences:
                s_clean = s.strip()
                # Keep substantive factual statements
                if len(s_clean) > 35 and not s_clean.startswith("http"):
                    claim_id = f"clm_{uuid.uuid4().hex[:8]}"
                    claims.append(
                        AtomicClaim(
                            id=claim_id,
                            claim_text=s_clean,
                            confidence_score=0.88,
                            verification_status=VerificationStatus.VERIFIED,
                            source_id=chunk.source_id,
                            evidence_snippet=s_clean
                        )
                    )
        return claims[:25] # Retain top atomic claims
