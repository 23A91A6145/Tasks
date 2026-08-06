# 🗂️ Project Plan — Approval-Gated Refund Agent (HITL)

> **One-line goal:** an AI agent that prepares refunds but cannot move money until a
> human approves — the reference implementation of the Human-in-the-Loop (HITL)
> safety pattern on the Microsoft Agent Framework approval semantics.

---

## 1. Executive Summary

| Item | Value |
|---|---|
| **Project** | Approval-Gated Refund Agent (HITL) |
| **Pattern** | Human-in-the-Loop · Sensitive-Tool Protection · AI Governance |
| **Framework** | Microsoft Agent Framework (`agent-framework-core`, `@tool(approval_mode="always_require")`) |
| **Stack** | Python 3.12+ · FastAPI · Pydantic · Uvicorn · Docker · Pytest |
| **LLM** | `mock` (default, offline) · `groq` (free tier) · `ollama` (local) |
| **Cost** | 100% free to build and run |
| **Status** | Complete — 36 tests passing, demo runner + DevUI verified |
| **Difficulty** | ⭐⭐⭐⭐ (Intermediate → Advanced) |

---

## 2. Vision & Objectives

**Vision:** demonstrate the single most important enterprise AI-safety pattern —
never let an autonomous agent perform an irreversible, high-risk action.

**Objectives**
1. Parse refund requests reliably (LLM or deterministic fallback).
2. Validate against safety policy (customer, order, amount, risk).
3. Intercept the sensitive payment tool behind an approval gate.
4. Pause/resume workflows via disk checkpoints (no lost state, no double-spend).
5. Let humans approve/reject/hold/escalate from a clean DevUI.
6. Leave an immutable audit trail and notify the customer.

---

## 3. Scope

### In scope ✅
- Chat-based refund intake (mock + optional Groq/Ollama).
- Policy engine, RBAC (Reviewer / Manager), rate limiting, SLA expiry.
- Approval DevUI with stats, queue, detail, timeline, logs, notifications.
- Audit logging, checkpointing, anti-fraud duplicate blocks.
- Tests, Docker deployment, documentation.

### Out of scope (now, tracked later) ❌
- Real payment gateway / bank integration.
- Real email/Slack/Teams delivery.
- PostgreSQL / Redis persistence.
- Production LLM-only parsing (no mock fallback).
- Multi-tenant auth (SSO) and org permissions.

---

## 4. How to Use

### 4.1 Install (any OS — local)
```bash
cd approval-gated-refund-agent
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # optional; defaults are safe
```

### 4.2 Run
```bash
python main.py            # DevUI → http://127.0.0.1:8000
```

### 4.3 Drive it three ways

**A) DevUI (recommended for demo)**
1. Open the dashboard. Send a prompt in the chat console (examples in §8).
2. The ticket appears in **Pending Queue**.
3. Switch reviewer: *Alice Smith (Reviewer)* or *Bob Johnson (Manager)*.
4. Approve / Reject / Hold / Escalate with notes.
5. Watch the timeline fill, the audit log grow, and the customer email preview appear.

**B) REST API**
```bash
# create a ticket
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Process a refund of $125 for CUST-1045 order ORD-5582 due to wrong item"}'

# decide (Approve/Reject/Hold/Escalate/Request More Info)
curl -X POST http://127.0.0.1:8000/api/approvals/REF-XXXX/decision \
  -H 'Content-Type: application/json' \
  -d '{"action":"Approve","notes":"verified","reviewer_name":"Bob Johnson","reviewer_role":"Manager"}'
```
Full endpoint table: `README.md §API`.

**C) Demo runner (headless, all scenarios)**
```bash
python run_demo.py
```
Runs 6 scenarios: auto-approve → pause → duplicate block → RBAC → resume → SLA expiry.

### 4.4 Choose an LLM mode (`.env`)
| `LLM_PROVIDER` | Requires | Behaviour |
|---|---|---|
| `mock` (default) | nothing | deterministic regex parsing, fully offline, always works |
| `groq` | `GROQ_API_KEY` | cloud extraction via Groq free tier; falls back to regex on failure |
| `ollama` | local `ollama` server | local extraction; falls back to regex on failure |

### 4.5 Tune policy (`.env`)
`MAX_AUTO_APPROVE_AMOUNT` (default 50) · `MANAGER_LIMIT` (100) · `APPROVAL_SLA_TIMEOUT_SECONDS` (300) · `RATE_LIMIT_PER_MINUTE` (120). Set `MAX_AUTO_APPROVE_AMOUNT=0` to force **every** refund through a human.

### 4.6 Verify
```bash
python -m pytest -q          # 36 tests
docker compose up --build -d # containerized (optional)
```

---

## 5. Where to Use

### Deployment targets
| Target | Command / notes |
|---|---|
| Local dev | `python main.py` |
| Docker | `docker compose up --build -d` (healthcheck on `/api/health`, volumes for logs/checkpoints) |
| Render / Fly / Railway (free) | containerize repo, start `python main.py`, set `.env` vars, attach volume |

### Real-world contexts the pattern maps to
Banking refunds · e-commerce returns/RMA · insurance claim payouts · loan approvals ·
healthcare prior authorizations · payroll corrections · government benefit payments ·
customer-support goodwill credits · any **enterprise AI copilot** that can take an
irreversible action.

---

## 6. Expectations

### What you should expect
- **Deterministic safety first:** the gate always blocks payment execution until a
  human approves — verified by the single-spend checkpoint, RBAC, and audit log.
- **Works offline, free, instantly:** no API key needed in `mock` mode.
- **Instant feedback in the DevUI:** queue auto-refreshes every 4s; decisions update
  stats, timeline, logs, and the notification inbox live.
- **Defined exceptions only:** the sole autonomous path is the small, configurable
  auto-approval carve-out (≤ `MAX_AUTO_APPROVE_AMOUNT`, Low risk, Active account).

### Behaviour matrix
| Situation | Expected behaviour |
|---|---|
| Missing customer/order/amount | `clarification_required` + list of missing fields |
| Unknown customer / wrong order owner | `policy_rejected` with reason |
| Amount > order total | `policy_rejected` |
| Duplicate active ticket | blocked (anti-fraud) |
| ≥ $100 or High-risk customer | Manager-only (403 for Reviewer) |
| Ticket pending > SLA | auto-`Expired`, checkpoint purged |
| Approve same ticket twice | rejected — already finalized |
| Malformed API body | `422` with field details |

### Performance expectations
- Parser: sub-millisecond in `mock` mode; LLM adds network latency only when enabled.
- Single-process, SQLite/JSON persistence → ideal for demo/portfolio, not multi-tenant scale.
- Rate limit: 120 req/min/IP (configurable).

### Non-goals / boundaries
- No real money movement, no real email sending, no SSO — simulated gateway + templates by design.
- JSON-file persistence is a demo store; move to PostgreSQL for production load.

---

## 7. Roles & Personas

| Persona | How they use it |
|---|---|
| **Customer / CSR** | submits requests via chat or API |
| **Reviewer (Alice Smith)** | handles low/medium-risk tickets ≤ `MANAGER_LIMIT` |
| **Manager (Bob Johnson)** | approves high-value/high-risk tickets, escalation endpoint |
| **Compliance / Audit** | reads `logs/audit.log`, decision history, system alerts |
| **Platform admin** | tunes `.env`, resets demo data via `POST /api/seed/reset` |
| **Data/Analytics** | consumes `/api/stats`, `/api/notifications`, `/api/approvals` |

---

## 8. Examples

### Sample prompts (copy-paste into the chat console)
| # | Prompt | Result |
|---|---|---|
| 1 | `Process a refund of $45 for CUST-1045 order ORD-5582 due to shipping mismatch` | ⚡ auto-approved |
| 2 | `Process a refund of $125 for CUST-1045 order ORD-5582 due to wrong item shipped` | 🛑 pending → Manager approves → executes |
| 3 | `Process a refund of $450 for CUST-2092 order ORD-8812 because no longer needed` | 🛑 Manager-only (Alice gets 403) |
| 4 | `Process a refund of $1500 for CUST-9912 order ORD-0001` | 🛑 High-risk, Manager-only |
| 5 | Same order again while #2 is pending | 🚫 duplicate block |
| 6 | `I want a refund` | ❓ clarification |

### API example (reject flow)
```bash
curl -X POST http://127.0.0.1:8000/api/approvals/REF-XXXX/decision \
  -H 'Content-Type: application/json' \
  -d '{"action":"Reject","notes":"Photos do not match condition","reviewer_name":"Alice Smith","reviewer_role":"Reviewer"}'
```
Expect: `{"status":"success","req_status":"Rejected", ...}` + rejection email template + audit entry.

---

## 9. Milestones & Timeline

| Phase | Deliverable | Status |
|---|---|---|
| **1. Foundation** | env setup, README, architecture doc | ✅ done |
| **2. Approval Workflow** | agent, sensitive tool, DevUI approval, demo | ✅ done |
| **3. Professional Features** | dashboard, profiler, decision form, notifications | ✅ done |
| **4. Production & Security** | settings, RBAC, rate limit, error handling, audit, tests | ✅ done |
| **5. Deployment & Portfolio** | Docker, GitHub, screenshots, demo GIF, portfolio docs | 🟡 GIF + publish remain |

**Suggested sprint plan (if building fresh):**
- **Sprint 1:** parsing + policy + sensitive tool + checkpoint. 
- **Sprint 2:** approval service + RBAC + DevUI + audit.
- **Sprint 3:** SLA, rate limiting, error handling, notifications.
- **Sprint 4:** tests, Docker, docs, portfolio polish.

---

## 10. Acceptance Criteria (Definition of Done)

- [ ] A refund cannot execute without an explicit human decision.
- [ ] Checkpoint persists on pause and is purged after finalization (no double-spend).
- [ ] RBAC blocks unauthorized approvers (403).
- [ ] Duplicate active claims are rejected.
- [ ] Every final decision lands in `logs/audit.log` with reviewer, role, IP, session, notes.
- [ ] Pending tickets expire per SLA and purge their checkpoint.
- [ ] `pytest` green (36 tests) and `run_demo.py` completes all 6 scenarios.
- [ ] DevUI renders stats, queue, detail, timeline, logs, notifications.
- [ ] Docker build runs and healthcheck passes.

---

## 11. Testing Strategy

- **Unit:** parser, policy engine, models, tool invariants, notifications, stats.
- **Integration:** agent→tool interception, decision→execution, rejection→cancellation,
  SLA timeout, RBAC, duplicate/double-approve.
- **API:** health, info, stats, chat, decision, outbox, 403/404/422 contracts.
- **Manual/E2E:** DevUI happy path + `run_demo.py`. Details: `docs/testing.md`.

---

## 12. KPIs to track

Approval SLA compliance (no ticket > timeout) · % auto-approved vs human-approved ·
mean review time · audit completeness (100% decisions logged) · unauthorized-access
attempts (logged in `errors.log`) · duplicate-claim blocks caught.

---

## 13. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Agent executes autonomously | gate + auto-approval is a tiny, configurable carve-out |
| Double payment from replay | single-spend checkpoint token |
| Under-qualified reviewer approves | RBAC + escalation path + audit |
| Stale tickets pile up | SLA lease auto-expiry + purge |
| Prompt injection changing amounts | strict input validation + policy ceiling + human notes |
| Key leakage | `.env` git-ignored, never logged |

---

## 14. Deliverables Checklist

- [x] `app/` modules (agent, refund_tool, approval, workflow, settings, config, models, services, middleware, utils)
- [x] `main.py` API + `templates/dashboard.html` DevUI
- [x] `tests/` (36 tests) · `run_demo.py`
- [x] `Dockerfile` + `docker-compose.yml` + `Makefile` + `.env.example` + `.gitignore`
- [x] `README.md` · `docs/` (architecture, workflow, security, testing, deployment, roadmap, plan, portfolio, socials)
- [x] screenshot of the DevUI in `docs/screenshots/dashboard.png`
- [ ] demo GIF + extra screenshots in `docs/screenshots/`
- [ ] GitHub publish + live link

---

## 15. Next Actions

1. ✅ DevUI screenshot captured (`docs/screenshots/dashboard.png`) — add a short GIF
   showing the approve→execute flow.
2. Push the repo to GitHub (see `docs/deployment.md §4`).
3. Add a free-tier Render/Fly deployment for a live demo link.
4. Optionally enable `groq`/`ollama` parsing and tune `MAX_AUTO_APPROVE_AMOUNT=0` for a strict demo.
5. Follow `docs/roadmap.md` Phase 5.3 backlog for production hardening.
