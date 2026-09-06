# 🚀 Startup Validator AI
### Evidence-Driven Multi-Agent Startup Validation & Decision-Support Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6.svg?logo=typescript)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC.svg?logo=tailwind-css)](https://tailwindcss.com)
[![SQLite](https://img.shields.io/badge/SQLite-aiosqlite-003B57.svg?logo=sqlite)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 1. The Core Paradigm Shift

Traditional AI startup tools suffer from **false precision**—prompting an LLM to invent arbitrary probabilities such as *"This startup has a 73% chance of success."* Startup outcomes in the real world depend on multidimensional external variables, data sparsity, unit economics, and competitive saturation.

**Startup Validator AI** transforms this paradigm:

$$\text{Validation Score} \ne \text{Probability of Success}$$

$$\textbf{Validation Output} = \textbf{Deterministic Score} + \textbf{Verifiable Evidence} + \textbf{Confidence Interval} + \textbf{Multidimensional Risks} + \textbf{Actionable Experiments}$$

Rather than acting as an oracle, the system provides **evidence-driven decision support**:
- **Overall Score**: e.g., `74 / 100` (Calculated deterministically across 10 transparent dimensions).
- **Decision Verdict**: `🟢 STRONG VALIDATE` | `🟡 VALIDATE WITH EXPERIMENTS` | `🟠 HIGH UNCERTAINTY` | `🔴 PIVOT / REWORK`
- **Confidence Calibration**: `HIGH` / `MEDIUM` / `LOW` based on citation authority and data completeness.
- **Falsifiable Experiments**: Prescribes specific smoke tests, landing page conversion thresholds, and customer interview protocols to de-risk assumptions before deploying engineering capital.

---

## 🏛️ 2. System Architecture

```
                 ┌───────────────────────────────────────────────┐
                 │          FOUNDER / DECISION MAKER             │
                 │         Idea + Category + ICP + Scope         │
                 └───────────────────────┬───────────────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │       FastAPI Orchestrator    │
                         │      Validation Flow Engine   │
                         └───────────────┬───────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            ▼                            ▼                            ▼
   ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
   │  Market Agent   │          │ Competitor Agt  │          │ Customer Agent  │
   │ TAM/SAM/Trends  │          │  Direct/Gaps    │          │ ICP/JTBD/WTP    │
   └────────┬────────┘          └────────┬────────┘          └────────┬────────┘
            │                            │                            │
            └────────────────────────────┼────────────────────────────┘
                                         │
                                         ▼ (Fan-in Context)
            ┌────────────────────────────┴────────────────────────────┐
            ▼                                                         ▼
   ┌─────────────────┐                                       ┌─────────────────┐
   │  Finance Agent  │                                       │   Risk Agent    │
   │ Unit Economics  │                                       │ 10-Dim Risk Map │
   └────────┬────────┘                                       └────────┬────────┘
            │                                                         │
            └────────────────────────────┬────────────────────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │      Product & Tech Critic    │
                         │    Feasibility & MVP Scope    │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │      Evidence Aggregator      │
                         │   Sources, Claims, Weights    │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │     Deterministic Scoring     │
                         │   10 Weighted Dimensions      │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │      Critic / Judge Agent     │
                         │   Consistency & Fact Check    │
                         └───────────────┬───────────────┘
                                         │
                              Disagreement > 20%?
                                 /             \
                               YES             NO
                                │               │
                                ▼               ▼
                         ┌─────────────┐ ┌─────────────┐
                         │ Re-Analysis │ │  Finalize   │
                         │ (Max 2 Lps) │ │   Dossier   │
                         └──────┬──────┘ └──────┬──────┘
                                └───────┬───────┘
                                        ▼
                         ┌───────────────────────────────┐
                         │      SQLite / History DB      │
                         │    Runs, Evidence, Metrics    │
                         └───────────────┬───────────────┘
                                         │
                                         ▼
                         ┌───────────────────────────────┐
                         │    React 18 + Vite SPA UI     │
                         │  SSE Stream, Visual Graph     │
                         └───────────────────────────────┘
```

---

## 🤖 3. The Seven Specialized Agents

| Agent | Responsibilities | Output Contract | Key Grounding Tools |
| :--- | :--- | :--- | :--- |
| **Market Research Agent** | TAM/SAM/SOM sizing, category CAGR growth, macro tailwinds, regulatory barriers | `MarketAnalysis` | Web search, Market Benchmarks |
| **Competitor Intelligence Agent** | Direct/indirect incumbents, pricing models, market saturation, unaddressed gaps | `CompetitorAnalysis` | Competitive Index, Feature Gap Matrix |
| **Customer Persona & ICP Agent** | Target buyer persona, Job-to-be-Done (JTBD), pain severity (0-100), willingness to pay | `CustomerAnalysis` | Customer Discovery Rubrics |
| **Financial Modeler Agent** | Unit economics (CAC/LTV, payback), 3-scenario projections (Conservative, Base, Optimistic) | `FinancialModel` | SaaS Cohort Economics Engine |
| **Product & Technical Critic** | Engineering feasibility, MVP scoping, third-party bottlenecks, timeline estimation | `ProductAnalysis` | Architecture Complexity Rubric |
| **Risk Matrix Agent** | 7-category risk breakdown (Competition, Financial, Regulatory, AI dependency) | `RiskAssessment` | Pre-Mortem Vulnerability Matrix |
| **Judge & Critic Agent** | Cross-examines agent claims, audits mathematical consistency, triggers re-analysis | `JudgeCritique` | Truth Arbiter & Consensus Audit |

---

## 📊 4. Deterministic 10-Dimension Scoring Model

Scores are **never** left to arbitrary LLM hallucination. Each dimension has an explicit mathematical weight summing to **100%**:

| Dimension | Weight | Target Signal Evaluated |
| :--- | :---: | :--- |
| **Problem Severity** | **15%** | Urgency and hair-on-fire nature of customer pain (0 = nice-to-have, 100 = critical blocker) |
| **Market Demand** | **15%** | TAM/SAM size, category CAGR, search momentum, and customer tailwinds |
| **Customer Fit & ICP** | **10%** | Alignment between value proposition, ICP workflow, and low switching costs |
| **Competitive Advantage** | **10%** | Ability to compete without being crushed by entrenched incumbents (Inverted rivalry) |
| **Differentiation & Moat** | **10%** | Proprietary workflow, specialized data flywheel, or network effects |
| **Monetization & Economics**| **10%** | LTV/CAC sustainability (>3:1 target), gross margins (>80%), and pricing power |
| **Distribution Feasibility**| **10%** | Predictable acquisition channels, organic referral loops, or viral coefficient |
| **Execution Feasibility** | **10%** | Realistic time-to-MVP (4-8 weeks), operational overhead, and capital efficiency |
| **Technical Feasibility** | **5%** | Architecture reliability, API dependency resilience, and minimal AI hallucination risk |
| **Risk Safety Index** | **5%** | Inverted composite risk index measuring resilience against market and regulatory shocks |
| **TOTAL** | **100%** | **Rigorous, reproducible evaluation vector** |

---

## 🧪 5. Actionable Validation Experiments

Instead of leaving founders with passive scores, the engine generates **falsifiable next experiments**:

1. **Smoke Test Landing Page & Pre-Signup Intent**
   - *Hypothesis*: $\ge 7\%$ of target students click "Request Early Access" when shown the core value proposition.
   - *Target Sample*: 150 targeted unique visitors.
   - *Action If Failed*: Modify hero messaging or adjust the core pitch.
2. **Customer Discovery & JTBD Problem Interviews**
   - *Target*: 20 1-on-1 interviews with target users.
   - *Success Metric*: $\ge 14/20$ confirm high-friction manual workarounds and request beta access.
3. **Concierge / Wizard-of-Oz Alpha Run**
   - *Target*: 15 active users completing the workflow manually assisted by the founder.
   - *Success Metric*: $\ge 60\%$ completion rate and NPS $\ge 50$.

---

## 💻 6. Quick Start & Installation

### Prerequisites
- **OS**: Ubuntu Linux, macOS, or Windows WSL2
- **Python**: 3.12+
- **Node.js**: v18+ (Node 24 recommended)
- **Local LLM (Optional)**: [Ollama](https://ollama.ai) with `ollama pull qwen3:4b-instruct` or `llama3.2:3b`

### 1. Clone & Setup Python Virtual Environment
```bash
git clone https://github.com/your-username/startup-validator-ai.git
cd startup-validator-ai

python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
*(Optional: Add `GROQ_API_KEY` or `GEMINI_API_KEY` to test cloud acceleration, or leave blank to use local Ollama / offline resilient intelligence).*

### 3. Build Frontend & Run Tests
```bash
# Build React Production Bundle
cd frontend
npm install
npm run build
cd ..

# Run Backend Pytest Suite
PYTHONPATH=. pytest backend/tests -v
```

### 4. Launch Service
```bash
# Easy launcher script
./scripts/start.sh

# Or start directly with Uvicorn (serves both React Frontend and FastAPI Backend)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at **`http://localhost:8000`** to access the dashboard!
For front-end development with Vite HMR:
```bash
cd frontend && npm run dev
# Accessible at http://localhost:5173 (proxied to backend on port 8000)
```

---

## 🎓 7. Research & Academic Paper Lab

Startup Validator AI includes a full academic evaluation engine that determines whether your startup’s core algorithmic, architectural, or empirical innovation qualifies for top-tier peer-reviewed publication:

1. **Publication Readiness & Chance (%)**: Calibrated score (30% to 96%) based on theoretical novelty, empirical rigor, reproducible datasets, and peer-review thresholds.
2. **Detailed Venue Matching**: Tailored fit scores, acceptance rates, review focus, and upcoming deadlines for top venues (NeurIPS, ICML, ICLR, KDD, ACM CHI, IEEE S&P, Nature Digital Medicine, etc.).
3. **What Needs to Be Added**: Explicit missing components required for acceptance (e.g., synthetic noise sensitivity, ablations against Baselines, multi-cohort trials, compute cost bounds).
4. **Additional Algorithmic Features**: Concrete architectural augmentations (e.g., AST-guided verification, dual-head uncertainty calibration, differential privacy guarantees).
5. **Step-by-Step Improvement Roadmap**: Prioritized milestones categorized by phase (Months 1–4) to elevate submission acceptance probability from baseline to 95%+.
6. **Compile-Ready IEEE LaTeX & BibTeX**: 1-click generation and copy/download of ready-to-compile `IEEEtran` manuscript draft and citation metadata.

---

## 📊 8. Startup Benchmarking & Gartner 2x2 Positioning

- **Pre-Loaded Curated Benchmarks**: Compare your startup instantly against battle-tested industry profiles such as `DevFlow AI` (Autonomous Code Review, Score 88.5) and `MediScribe AI` (Ambient Clinical EHR Scribe, Score 84.2).
- **Gartner 2x2 Positioning Matrix**: Interactive quadrant chart mapping **Market Execution vs. Innovation Novelty** (Market Leaders, Visionaries, Challengers, Niche Players).
- **Cross-Metric Radar & Comparison Tables**: Compare differentiation moats, LTV/CAC, payback periods, customer pain urgency, and research publishability side-by-side.

---

## 🐳 9. Docker Deployment

Launch the full stack with a single command:
```bash
docker-compose up --build
```
This starts the multi-stage containerized FastAPI service with the embedded React SPA on port `8000`.

---

## 🔌 10. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/validations` | Submits startup idea and initiates asynchronous multi-agent flow |
| `GET` | `/api/v1/validations/stream/{run_id}` | Server-Sent Events (SSE) streaming real-time agent execution events |
| `GET` | `/api/v1/validations/{run_id}` | Retrieves complete structured validation dossier (`ValidationReport`) |
| `GET` | `/api/v1/validations/{run_id}/export` | Exports dossier in `markdown` or `json` format |
| `GET` | `/api/v1/validations/{run_id}/paper` | Exports full academic LaTeX manuscript and BibTeX package |
| `GET` | `/api/v1/validations/{run_id}/pitch-deck` | Exports structured 10-slide VC pitch deck JSON |
| `GET` | `/api/v1/history/benchmarks` | Returns curated market benchmark reports for comparative positioning |
| `DELETE`| `/api/v1/validations/{run_id}` | Deletes validation record and cascades related tables |
| `GET` | `/api/v1/history` | Chronological list of all evaluated startups |
| `GET` | `/api/v1/history/compare?run_ids=...` | Side-by-side comparative analysis of up to 4 startups (supports benchmark IDs) |
| `GET` | `/api/v1/analytics/summary` | Platform metrics (average scores, category distribution, latency) |
| `GET` | `/api/v1/health` | Service health, version, and database connection status |
| `GET` | `/api/v1/models/status` | Real-time status of local Ollama models and cloud routing |

---

## 🛡️ 9. Security & OWASP Agentic Guidelines

Aligned with **OWASP 2026 Agentic Application Standards**:
- **Tool Allowlists**: Agents have strict, typed tool permission boundaries (no arbitrary shell, no unrestricted filesystem, no database deletion).
- **Strict Pydantic Validation**: All agent reasoning is parsed through strongly-typed Pydantic schemas.
- **Loop Boundedness**: Maximum of 2 re-analysis iterations to prevent runaway token costs or infinite execution cycles.
- **Air-Gapped Resiliency**: Resilient offline research databases ensure deterministic execution even during network outages.

---

## 📄 License
MIT License. Created for founders, accelerators, product managers, and venture researchers.
