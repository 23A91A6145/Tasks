# ADR 001: Hybrid Dense + Sparse Retrieval via Reciprocal Rank Fusion (RRF)

## Status
Accepted

## Context
Standard naive RAG relying solely on vector embeddings struggles to retrieve exact tokens such as library version strings, error codes, CVE identifiers, and specific model parameter counts. Conversely, pure BM25 lexical search misses conceptual synonyms and semantic paraphrase.

## Decision
We implement a hybrid retrieval pipeline using Reciprocal Rank Fusion (RRF) with constant $k = 60$:
$$\text{RRF\_Score}(d) = \sum_{m \in \{\text{dense}, \text{sparse}\}} \frac{1}{k + \text{rank}_m(d)}$$

## Consequences
- Guaranteed preservation of exact keyword matches and semantic concepts.
- Resilient to embedding model drift on CPU-only local environments.
- Zero extra licensing or API costs.
