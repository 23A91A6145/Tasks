# Roadmap — Volume 1 & 2 (what we do now)

## Volume 1 — Foundation (done)

### Phase 1.1 — Product Planning (`docs/`)
- PRD, architecture, DB model, feature matrix, this roadmap.

### Phase 1.2 — Project Setup
- Monorepo layout, Python venv, Node modules, `.env.example`, Docker Compose, scripts.

### Phase 1.3 — Authentication & Multi-Tenancy (backend)
- JWT auth, bcrypt, RBAC, workspace CRUD, members, audit log, super admin.

### Phase 1.4 — Professional UI/UX (frontend)
- Landing, login/register, dashboard shell, users/settings/billing, dark/light theme.

## Volume 2 — AI Support (done)

### Phase 2.1 — AI engine ladder
- `crewai` / `llm` / `fallback` selection in `app/agents/engine.py`; zero-key operation by default.

### Phase 2.2 — Per-tenant knowledge & RAG
- `knowledge_service`, hash/openai/local embeddings, numpy/qdrant vector stores,
  upload / URL / FAQ ingestion, semantic search with scores, tag counts, delete.

### Phase 2.3 — Ticket triage + hierarchical crew
- `ticket_service` + `crew_support` (manager + router + knowledge + support + escalation agents);
  direct & fallback engines mirror the same semantics; sources + confidence captured.

### Phase 2.4 — Checkpointed workflows
- `flows/runner` + `ticket_flow` / `escalation_flow` / `feedback_flow`;
  `awaiting_approval` → resume (approve publishes, reject discards); audit trail.

### Phase 2.5 — Volume 2 UI
- Knowledge (upload/search/tags/delete), Tickets (thread + Handle-with-AI + approval card),
  Flows (runs + resume), Agents (engine status + crew config).

- **Verify:** `bash scripts/setup-ai.sh` (optional) · `cd apps/backend && .venv/bin/pytest -q`
- **Verify:** `cd apps/frontend && npm run typecheck && npm run build`
- **Demo:** zero-key — upload a FAQ, search it, handle a ticket; try a "urgent" ticket for the approval checkpoint.

## Definition of Done (Volume 1)
- [x] Backend test suite green
- [x] Frontend production build green
- [x] Register → create workspace → invite member → see activity on dashboard
- [x] Foreign workspace returns 403
- [x] Role changes enforced (agent cannot edit workspace settings)
- [x] `docker compose up --build` runs the full stack

## Definition of Done (Volume 2)
- [x] Backend suite green on `.venv` and `.venv312` (34 tests incl. CrewAI smoke test)
- [x] Frontend `typecheck` + production `build` green
- [x] Zero-key demo: register → workspace → FAQ → search → handle a ticket
- [x] Urgent ticket pauses at `awaiting_approval` → approve → reply published + ticket resolved
- [x] Tenant A knowledge never answers tenant B (isolation test green)

## Coming up
- **Volume 3** — RAG (Qdrant), MCP servers, tool ecosystem
- **Volume 4** — plans & usage limits, long-running jobs, analytics
- **Volume 5** — product polish, free-tier deployment, portfolio docs
