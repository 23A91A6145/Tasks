# ResearchOS System Architecture

ResearchOS adopts a deterministic and agentic hybrid pipeline that prioritizes auditability, predictability, and citation integrity.

```
                         USER REQUEST
                              │
                              ▼
                     ┌──────────────────┐
                     │ Research Intake  │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Research Planner │
                     └────────┬─────────┘
                              │
                    Decomposed Sub-Vectors
                     /        │        \
                    ▼         ▼         ▼
               OpenAlex     arXiv     Web Search
                    \         │         /
                     ▼        ▼        ▼
                     ┌──────────────────┐
                     │  Source Filter   │
                     │   & Deduplicator │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  Hybrid RRF RAG  │
                     │  (BM25 + Dense)  │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Evidence & Claim │
                     │ Extractor Engine │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ 4-Tier Citation  │
                     │ Grounding Engine │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │    Synthesizer   │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │   Critic Agent   │
                     └────────┬─────────┘
                              │
                        Passes Audit?
                        /           \
                      NO             YES
                      │               │
                  Re-Search           ▼
                      │       Final Technical Report
                      └─────── (With Verified Citations)
```

## Core Modules
1. `backend/app/agents/planner.py`: Decomposes user queries into orthogonal research angles.
2. `backend/app/sources/`: Free-tier connectors to arXiv, OpenAlex, Semantic Scholar, and Tavily/Brave.
3. `backend/app/retrieval/hybrid.py`: Hybrid Reciprocal Rank Fusion ($k=60$) combining BM25 and CPU semantic embeddings.
4. `backend/app/research/claims.py`: Atomic factual claim extraction.
5. `backend/app/research/citations.py`: 4-tier citation verification (HTTP health, passage existence, semantic cosine similarity, hallucination check).
6. `backend/app/agents/synthesizer.py`: High-density technical writing engine with inline citations.
7. `backend/app/agents/critic.py`: Automated quality audit triggering replanning when score < 80.
