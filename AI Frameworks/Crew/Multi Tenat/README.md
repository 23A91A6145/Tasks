# TenantDesk AI — Multi-Tenant AI Support Platform

> Production-grade AI SaaS capstone: every company gets its own AI support crew, isolated
> knowledge base and workspace. **All 5 volumes are implemented and tested — auth +
> multi-tenancy, AI support crew, RAG + MCP, plans/jobs/analytics/public widget, and the
> admin console — and it runs on a laptop with zero API keys.**

> 🏁 **Final conclusion + docs:** see [`docs/FINAL-CONCLUSION.md`](docs/FINAL-CONCLUSION.md)
> for the GitHub/social-ready summary and [`docs/09-final-guide.md`](docs/09-final-guide.md)
> for the full technical walkthrough with verified examples.

## What's inside

| Piece | Tech | Status |
|---|---|---|
| Frontend | Next.js 15 · React 19 · Tailwind CSS v4 | ✅ Vol 1–4 |
| Backend | FastAPI · SQLAlchemy 2 · pydantic v2 | ✅ Vol 1–4 |
| Auth | JWT (access + refresh) · bcrypt | ✅ |
| Tenancy | Workspaces, members, RBAC, tenant isolation | ✅ |
| AI crew | CrewAI hierarchical crew (optional) → direct LLM → offline rule engine | ✅ auto-select |
| Knowledge | Per-tenant RAG: upload/URL/FAQ/raw text, semantic search, tags, Qdrant | ✅ Vol 2 + 3 |
| MCP & tools | MCP server connectivity + tool ecosystem | ✅ Vol 3 |
| Tickets | Triage, AI drafts with sources, human approval checkpoints | ✅ |
| Flows | Checkpointed, resumable workflows (ticket / escalation / feedback) | ✅ |
| Plans & quotas | Free / Pro / Enterprise catalog, monthly request/doc/seat/storage limits | ✅ Vol 4 |
| Jobs | Long-running jobs with progress, checkpoints and retry (DB-queue ready) | ✅ Vol 4 |
| Analytics | Requests, tokens, cost, tickets, knowledge growth, agent performance | ✅ Vol 4 |
| Public widget | Token-gated chat + ticket handoff embeddable on any site | ✅ Vol 4 |
| Webhooks | HMAC-signed outbound events (`ticket.created`, `ticket.ai_handled`) | ✅ Vol 5 |
| Admin console | `/admin` — platform KPIs, plan catalog, all tenants (super admins) | ✅ Vol 5 |
| Audit | Activity log on every action, incl. AI decisions | ✅ |
| Security | Cross-tenant ai-handle blocked, quota enforced on jobs, MCP filesystem sandboxed | ✅ 4 regression tests |
| Tests | 65 pytest cases (auth, RBAC, isolation, RAG, flows, crew, plans, jobs, analytics, admin, webhooks, security, password reset) + 5 Playwright E2E | ✅ passing |
| Deploy | Docker Compose (Postgres + API + worker + Web) · free-tier friendly | ✅ |

## Quick start (laptop, everything free)

Prereq: Python 3.12+, Node 20+, and optionally Docker.

**One command — setup → seed → super admin → tests → run everything:**
```bash
bash scripts/launch.sh
```

Or step by step:

```bash
# 1) one-time setup (venv + deps + .env files)
bash scripts/setup.sh

# 2) run backend (8000) + frontend (3000) together
bash scripts/dev.sh
```

Open http://localhost:3000 → Register → create a workspace → try the **AI Platform**:
add an FAQ to Knowledge, search it, then open **Tickets** and hit **Handle with AI**.

- API docs (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Enable the full CrewAI crew (optional)

```bash
bash scripts/setup-ai.sh          # Python 3.12 venv + CrewAI
# add OPENAI_API_KEY (or an OpenAI-compatible base URL) to apps/backend/.env
bash scripts/dev.sh               # dev.sh prefers the CrewAI venv
```

Without this, the engine still works end-to-end via the offline rule engine — no key, no cost.

### Seed demo data (optional)

```bash
apps/backend/.venv/bin/python scripts/seed.py
# logins: owner@demo.com / admin@demo.com / agent@demo.com — password: demo-password-123
```

### One-click demo (no account needed)

The first time anyone calls it, the shared demo workspace ("Acme Support") is provisioned
on demand — users, FAQ knowledge, tickets, agents, widget, flows, jobs and 15 days of usage
history. Idempotent and self-healing, so it works on a completely empty database.

```bash
curl -X POST http://localhost:8000/api/v1/auth/demo   # → access + refresh tokens
```

Or click **"Open live demo"** on the homepage / login page — you land straight in the app.

### Platform admin console (optional)

```bash
apps/backend/.venv/bin/python -m scripts.create_superadmin you@example.com [--password secret]
# → then log in and open /admin (overview + all tenants). See docs/09-final-guide.md.
```

### Run tests & checks

```bash
cd apps/backend && .venv/bin/pytest -q            # 64 tests (crew skipped on 3.14)
cd apps/backend && .venv312/bin/pytest -q         # 65 tests incl. CrewAI smoke test (3.12)
cd apps/frontend && npx tsc --noEmit && npx next build
cd e2e && npx playwright test                     # 5 E2E smoke tests (needs :8000 + :3000)
```

### Docker Compose (Postgres + full stack)

```bash
docker compose up --build                 # db + backend + worker + frontend

# optional: include CrewAI (larger image, needs an LLM key at runtime)
docker compose build --build-arg INSTALL_AI=1
docker compose up
```

The worker starts with the stack by default (jobs are DB-backed with checkpoints), so
jobs created via the API are processed without extra flags.

## API surface (v1)

Auth & tenancy:
```
POST   /api/v1/auth/demo            one-click demo login (provisions on first call)
POST   /api/v1/auth/register        create account (+ optional workspace)
POST   /api/v1/auth/login           login → access + refresh tokens
POST   /api/v1/auth/refresh         rotate access token
POST   /api/v1/auth/forgot-password request a password-reset link (enumeration-safe)
POST   /api/v1/auth/reset-password  set a new password with the reset token (single use)
GET    /api/v1/auth/me              current user
POST   /api/v1/workspaces           create workspace
GET    /api/v1/workspaces           list my workspaces
GET/PATCH/DELETE /workspaces/{slug} view / update / delete (owner)
GET    /workspaces/{slug}/members   list members
POST   /workspaces/{slug}/members   invite by email
PATCH/DELETE /workspaces/{slug}/members/{userId}  change role / remove
GET    /workspaces/{slug}/activity  audit feed
GET    /workspaces/{slug}/stats     dashboard KPIs
GET    /api/v1/admin/overview       platform overview (super admin)
GET    /api/v1/admin/workspaces     all tenants + plans (super admin)
```

Platform super admins are created with `scripts/create_superadmin.py` (see the Quick start →
**Platform admin console**); the guard is `User.is_super_admin` + `get_current_super_admin`.

AI support (all tenant-scoped, see `docs/06-volume2-ai-support.md`):
```
GET/POST      /workspaces/{slug}/knowledge            list / upload (multipart)
POST          /workspaces/{slug}/knowledge/search     semantic search (top-k, scores)
DELETE        /workspaces/{slug}/knowledge/{id}       delete + drop vectors
POST          /workspaces/{slug}/knowledge/ingest-url  fetch public URL
POST          /workspaces/{slug}/knowledge/faq         add Q&A doc
GET           /workspaces/{slug}/knowledge/tags        tag counts
GET/POST      /workspaces/{slug}/tickets              list / create
GET           /workspaces/{slug}/tickets/{id}         detail (messages)
POST          /workspaces/{slug}/tickets/{id}/messages add a reply
POST          /workspaces/{slug}/tickets/{id}/ai-handle  run the AI crew → draft + flow
GET           /workspaces/{slug}/flows                recent runs
POST          /workspaces/{slug}/flows/trigger        escalation / feedback flows
POST          /workspaces/{slug}/flows/{id}/resume    approve / reject a human checkpoint
GET/PATCH     /workspaces/{slug}/agents               list / configure crew agents
GET           /workspaces/{slug}/agents/engine        active engine + capability status
GET           /workspaces/{slug}/tools                tool catalog (category filter)
POST          /workspaces/{slug}/tools/execute        run a built-in tool
GET           /workspaces/{slug}/mcp/servers          registered MCP servers + tools
POST          /workspaces/{slug}/mcp/call             invoke an MCP tool
```

Volume 4 — plans, jobs, analytics, public widget:
```
GET           /workspaces/{slug}/billing/summary      plan, period, usage vs limits, catalog
POST          /workspaces/{slug}/billing/change       switch plan (owner)
GET           /workspaces/{slug}/analytics/overview   one payload for the analytics page
GET/POST      /workspaces/{slug}/jobs                 list / create a job (runs + retries)
POST          /workspaces/{slug}/jobs/{id}/retry      resume a failed job from its checkpoint
DELETE        /workspaces/{slug}/jobs/{id}            delete a job
POST          /workspaces/{slug}/widget/enable        generate the public widget token (owner)
GET           /workspaces/{slug}/widget/config        widget token + embed URL
POST          /workspaces/{slug}/widget/rotate        rotate the widget token (owner)
POST          /workspaces/{slug}/widget/disable       revoke the widget (owner)
POST          /public/{slug}/chat                     unauthenticated widget chat (X-Widget-Token)
POST          /public/{slug}/tickets                  widget → human ticket handoff
GET           /workspaces/{slug}/webhooks             current webhook config (owner/admin)
POST          /workspaces/{slug}/webhooks             set URL + HMAC secret + events
POST          /workspaces/{slug}/webhooks/test        send a test.ping to your endpoint
```

Job types (`POST /jobs`): `index_document` (re-index), `crawl_website`, `batch_faq`,
`weekly_report`. Set `JOBS_INLINE=0` on the backend and run a worker
(`python -m scripts.worker` or the `worker` compose profile) to move execution off the request
path — the API contract doesn't change.

Plans are enforced server-side on knowledge uploads/search, AI ticket handling, widget chat and
member invites. Monthly usage resets on the workspace billing date.

## How the AI engine picks itself

```
AI_ENGINE=auto  →  crewai (installed + key)  →  llm (OpenAI-compatible)  →  fallback (free, offline)
```

Every engine returns the same `HandleResult` (draft, classification, priority, summary,
sources, escalate, confidence), so flows and the UI are engine-agnostic. Knowledge search is
scoped to the tenant's own namespace — cross-tenant retrieval is impossible.

## Role hierarchy

```
owner → admin → manager → agent → user        (+ platform super_admin)
```
All endpoints enforce minimum-role checks; tenant access is proven by membership
(no client-supplied tenant ID is trusted).

## Project layout

```
apps/backend   FastAPI app (app/{core,models,schemas,services,agents,flows,tools,mcp,api}, tests/)
apps/frontend  Next.js app (landing, auth, /app/* dashboard shell, /admin console, /widget-demo)
apps/admin     platform admin-API notes (console is in-app at /admin)
docs/          5-volume plan + PRD + architecture + DB model + Vol 2/4/5 specs + final guide
scripts/       setup.sh · setup-ai.sh · dev.sh · launch.sh · seed.py
{agents,knowledge,flows,services,workers,database,mcp,tools}/   root bridge packages
docker-compose.yml
```

## Roadmap

- **Volume 1** ✅ — Auth, multi-tenancy, RBAC, audit
- **Volume 2** ✅ — CrewAI hierarchical crew, checkpointed flows, per-tenant knowledge
- **Volume 3** ✅ — RAG (Qdrant), MCP servers, tool ecosystem
- **Volume 4** ✅ — plans & usage limits, long-running jobs, analytics, public widget
- **Volume 5** ✅ — product polish, free-tier deployment, portfolio docs

See `docs/00-project-plan.md` for the full detailed plan, `docs/FINAL-CONCLUSION.md` for the
GitHub/social-ready final conclusion, and `docs/09-final-guide.md` for the full technical
walkthrough (run commands, feature-by-feature usage, sample end-to-end example, open work and
expectations).
