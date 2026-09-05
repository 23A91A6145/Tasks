# 4-Tier Citation Grounding Specification

## Tier 1: Link & Domain Validation
- Asynchronous HTTP HEAD/GET request ensuring HTTP 200 OK and valid domain formatting.

## Tier 2: Passage Existence Grounding
- Verifies that the quoted excerpt in the report is an exact or high-token-overlap substring of the retrieved document.

## Tier 3: Semantic Alignment
- Computes cosine similarity between the synthesized claim and the supporting passage (threshold $\ge 0.75$).

## Tier 4: Contradiction & Hallucination Auditing
- Evaluates whether the primary assertion is supported or contradicted, returning a composite factual support score.
