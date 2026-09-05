# ResearchOS: Production Agentic AI Research Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-9%2F9%20Passing-brightgreen.svg)]()
[![Free Tier Friendly](https://img.shields.io/badge/Cost-%240.00%20Free%20Tier-success.svg)]()

> **ResearchOS** is an enterprise-grade autonomous research platform built on Ubuntu Linux that converts complex inquiries into publication-grade, citation-grounded technical reports. It combines deterministic high-performance retrieval and vector ranking with an agentic state graph for research planning, atomic claim extraction, 4-tier citation verification, and self-reflective critique.

---

## 🎯 Architecture & Hybrid Workflow

ResearchOS explicitly rejects naive "LLM + search API" loops in favor of a deterministic and agentic hybrid pipeline:

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
---
## 🖥️ Production 3-Panel Workspace UI

The frontend is a dark research-lab interface designed for information density and interactive citation auditing:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ ResearchOS v0.1                     🔍 Search Collections    ⚙ Settings   ● Active│
├───────────────┬──────────────────────────────────────────┬───────────────────────┤
│ WORKSPACES    │           RESEARCH REPORT                │     AGENT TRACE       │
│               │                                          │                       │
│ + New Run     │ Multi-Agent Frameworks in 2026           │ Total: 4,820 ms       │
│               │ ──────────────────────────────────────── │ ───────────────────── │
│ AI Agents     │ Executive Summary                        │ ● Research Planner    │
│ RAG & Memory  │ Modern multi-agent system engineering... │   Duration: 42 ms     │
│ Cloud Systems │ requires durable checkpointing [1].      │ ● Multi-Source Search │
│               │                                          │   arXiv: 3 papers     │
│ PAST RUNS     │ Comparative Evaluation Matrix            │   OpenAlex: 3 works   │
│               │ ┌───────────┬────────────┬─────────────┐ │   Web: 3 resources    │
│ ● LangGraph   │ │ Dimension │ LangGraph  │ CrewAI      │ │ ● Hybrid RRF Ranking  │
│   vs CrewAI   │ ├───────────┼────────────┼─────────────┤ │   k=60 (Dense+Sparse) │
│ ● MCP Security│ │ State     │ Checkpoint │ Conversat.  │ │ ● Claim Extraction    │
│ ● Vector DBs  │ └───────────┴────────────┴─────────────┘ │   24 Atomic Claims    │
│               │                                          │ ● 4-Tier Verification │
│               │ Production Recommendations               │   Link Health: 100%   │
│               │ 1. Adopt graph state machines...         │   Factual Ground: 92% │
│               │ 2. Use 4-tier citation verification...   │ ● Report Synthesis    │
│               │                                          │ ● Critic Fact-Check   │
│               │ Verified Annotated Bibliography          │   Score: 92/100 (PASS)│
│               │ [1] LangGraph Checkpointing Architecture │                       │
│               │     Link Valid: 200 OK | Grounding: 94%  │ Sources: 12           │
│               │     Passage: "cyclical graph execution..."│ Claims: 24 | Cit.: 18 │
└───────────────┴──────────────────────────────────────────┴───────────────────────┘
```

---

## 🛡️ The 4-Tier Citation Verification Engine

Recent deep-research benchmarks demonstrate that LLMs frequently invent citations or attribute genuine facts to unrelated URLs. ResearchOS guarantees citation provenance through 4 sequential verification tiers:

| Tier | Verification Check | Enforcement Mechanism |
| :--- | :--- | :--- |
| **Tier 1** | **Link & Domain Health** | Asynchronous HTTP HEAD/GET request verifies $200\text{ OK}$, valid DNS, and reachable hosts. |
| **Tier 2** | **Passage Grounding** | Validates that the quoted excerpt is a verbatim or high-overlap substring of the retrieved document. |
| **Tier 3** | **Semantic Vector Alignment** | Computes cosine similarity between the synthesized claim and the quoted passage ($\text{threshold} \ge 0.75$). |
| **Tier 4** | **Hallucination Defense** | Calculates factual support index and flags over-extrapolations or contradictions. |

---

## 💰 100% Free & Open-Source Tier Ecosystem

ResearchOS is engineered specifically for standard Linux laptops (tested on Ubuntu with Intel i7, 16GB RAM, CPU-only):

* **Academic Connectors (100% Free)**:
  * **OpenAlex API**: 100,000 requests/day free with polite pool email.
  * **arXiv Public API**: Free preprint search across computer science and AI.
  * **Semantic Scholar**: Free academic graph query API.
* **Web Search**:
  * **Tavily Search**: 1,000 free API queries/month.
  * **Brave Search API**: $5 free credit/month.
  * **Deterministic Fallback**: Built-in high-credibility offline knowledge base for zero-credential development.
* **Inference Options**:
  * **Local CPU**: Native integration with [Ollama](https://ollama.ai) (`mistral`, `llama3.2`).
  * **Cloud Free-Tier**: Google Gemini API free-tier.
* **Storage & Vectors**:
  * Dual-mode database: local zero-config **SQLite** out-of-the-box, or **PostgreSQL 16 + pgvector** via Docker.

---

## 🗺️ The Complete 5-Volume, 25-Phase Roadmap

| Volume | Phase | Description |
| :--- | :---: | :--- |
| **Volume 1: Foundation** | 1 | Product requirements & 5 research modes (Quick, Deep, Academic, Comparison, Competitive) |
| | 2 | Deterministic vs. Agentic architecture boundaries |
| | 3 | Ubuntu CPU development environment configuration |
| | 4 | Repository skeleton, packaging with `uv`, and linting standards |
| | 5 | Relational & `pgvector` database schema design |
| **Volume 2: Hybrid RAG** | 6 | Free source connectors (arXiv, OpenAlex, Semantic Scholar, Tavily, Brave) |
| | 7 | Document normalization, hierarchical chunking & SHA-256 deduplication |
| | 8 | Hybrid Reciprocal Rank Fusion (RRF $k=60$) combining BM25 and dense vectors |
| | 9 | Multi-workspace knowledge collections |
| | 10 | Baseline retrieval evaluation benchmark (Recall@5, Precision@5, MRR) |
| **Volume 3: Agents** | 11 | Research Planner & sub-question orthogonal decomposition |
| | 12 | Autonomous multi-source concurrent retrieval agent |
| | 13 | Loop guards & safety boundaries (`MAX_STEPS = 25`, `MAX_TIME = 300s`) |
| | 14 | Atomic claim extraction & passage provenance engine |
| | 15 | Publication-grade Research Synthesizer |
| **Volume 4: Trust & Security**| 16 | 4-Tier Citation Verification Engine |
| | 17 | Empirical Ragas-aligned evaluation framework (`DeepResearchBench`) |
| | 18 | Self-Reflective Critic agent & quality audit gate |
| | 19 | OWASP GenAI Top 10 security: SSRF blocking & XML data fencing |
| | 20 | Step-by-step latency & token observability tracing |
| **Volume 5: Production UI** | 21 | High-density dark research laboratory UI design system |
| | 22 | 3-Panel React workspace layout |
| | 23 | Live agent step streaming & node transition graph |
| | 24 | Interactive citation popovers with verification badges |
| | 25 | Docker Compose orchestration, automated tests & CI/CD |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Linux OS (Ubuntu 20.04/22.04/24.04 recommended)
- Python 3.10+
- Node.js 18+ & npm
- `uv` Python project manager

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. One-Command Setup
```bash
git clone https://github.com/your-username/research-os.git
cd research-os
./scripts/setup.sh
```

### 3. Run Automated Tests
```bash
./scripts/test.sh
```
```
============================== 9 passed in 5.91s ===============================
- test_end_to_end_research_pipeline: PASSED
- test_api_health_endpoint: PASSED
- test_api_research_endpoint: PASSED
- test_citation_passage_grounding: PASSED
- test_link_health_validation: PASSED
- test_bm25_retrieval: PASSED
- test_hybrid_rrf_retrieval: PASSED
- test_ssrf_prevention: PASSED
- test_untrusted_content_sanitization: PASSED
```

### 4. Launch Full-Stack Application
```bash
./scripts/run.sh
```
* **Frontend UI**: [http://localhost:5173](http://localhost:5173)
* **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
* **Interactive OpenAPI / Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 REST API Examples

### Execute an Autonomous Research Run
```bash
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Compare LangGraph, CrewAI and Microsoft Agent Framework in 2026",
    "mode": "deep",
    "max_sources": 20
  }'
```

### Run Empirical Grounding Evaluation
```bash
curl -X POST http://localhost:8000/api/v1/research/{run_id}/evaluate
```

---

## 🔒 Security & OWASP GenAI Compliance
ResearchOS strictly implements defenses against the OWASP Top 10 for LLMs:
1. **Untrusted Data Boundary**: Scraped web pages and academic snippets are encapsulated in `<source_data>` XML fences to neutralize Indirect Prompt Injections (`IGNORE PREVIOUS INSTRUCTIONS`).
2. **SSRF Filter**: `SecuritySanitizer.validate_url_safety()` rejects loopback addresses (`127.0.0.1`, `localhost`), private RFC1918 subnets (`10.0.0.0/8`, `192.168.0.0/16`), and non-HTTP protocols.
3. **Loop Bound Guards**: Strict caps prevent runaway agent execution (`MAX_STEPS = 25`, `MAX_SEARCHES = 12`, `MAX_RUNTIME = 300s`).

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
