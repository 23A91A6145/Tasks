# Volume 4 — Plans, Long-Running Jobs, Analytics & the Public Widget

**Goal:** turn the working AI support platform into a monetizable SaaS. Every tenant gets plan
limits that are *enforced* (not just displayed), long-running work becomes resumable jobs, and
the platform exposes usage analytics plus an embeddable public widget — all still free to run.

## 1. Plans & usage limits (`app/services/plans.py`)

One shared `PLANS` catalog drives both the billing API and every enforcement check:

| Plan | Price | AI requests/mo | Docs | Seats | Storage | Priority | Advanced analytics |
|---|---|---|---|---|---|---|---|
| free | $0 | 500 | 10 | 5 | 100 MB | — | — |
| pro | $49 | 5,000 | 100 | 50 | 2 GB | ✅ | ✅ |
| enterprise | $299 | unlimited | unlimited | unlimited | unlimited | ✅ | ✅ |

Key design points:

- **`0` means unlimited** — `is_unlimited()` makes the catalog self-describing and avoids
  `float("inf")` leaking into JSON.
- **Monthly period anchored to `org.created_at`** (`period_start()`), so free-trial tenants get a
  full month regardless of signup day; no calendar month drift.
- **Enforcement helpers** (`check_request_quota`, `check_knowledge_quota`, `check_seat_quota`)
  raise `HTTPException(429)` with actionable messages. Wired into: knowledge upload/URL/FAQ,
  knowledge search, AI ticket handling, widget chat, and member invites.
- **Metering** is a single `usage` helper (`usage.track(db, org, kind, tokens)`) called from
  the AI entry points (ticket flow, escalation flow, feedback flow, knowledge search, widget).
  Kind strings (`ai.handle_ticket`, `ai.search`, `ai.weekly_report`, `ai.widget_chat`) feed the
  analytics `by_kind` breakdown.
- `billing_summary()` returns everything the Billing page needs in one call: plan, period,
  usage-vs-limit meters, and the full catalog for plan switching.

## 2. Long-running jobs (`app/services/jobs.py`)

The `jobs` table (alembic `0002`) persists async work with progress + checkpoints:

```
id, organization_id, job_type, status (queued|running|completed|failed),
label, current_step, total_steps, progress (0-100),
input_data, checkpoint, result, error, created_by_id, timestamps
```

Four job types:
- **`index_document`** — rebuilds chunks for one document through the RAG pipeline.
- **`crawl_website`** — bounded crawler (`max_pages`, domain-scoped) that ingests each page as
  a URL document, saving progress + `visited`/`pending` in the checkpoint.
- **`batch_faq`** — ingests one or many FAQ entries in a single job.
- **`weekly_report`** — aggregates the last 7 days of `UsageRecord` into a Markdown digest.

Design points:

- **Checkpoint-first.** Each `_progress()` persists `progress`, `current_step` and a JSON
  `checkpoint`. A failed job is retried *from its checkpoint*, not from scratch — the crawler
  resumes with its `visited` set, the FAQ batch skips already-ingested items.
- **Idempotent `run_job`.** Completed jobs are no-ops; failed jobs re-enter the handler.
- **Worker-ready.** `JOBS_INLINE=1` (default) runs inline for zero-infra dev; `JOBS_INLINE=0`
  leaves jobs queued and a background worker (`python -m scripts.worker`, or the `worker`
  compose profile) polls and executes them. Redis/Celery can be dropped in behind the same
  contract — the API surface never changes.

## 3. Analytics (`app/services/analytics.py`)

Aggregations are scoped to `organization_id` server-side (never in the client):

- `summary()` — KPI cards: monthly requests vs limit, tokens, estimated cost
  (gpt-4o-mini-class `COST_PER_MILLION`), open tickets, 7-day resolution rate, storage, agents.
- `usage_series()` — daily request/token series + `by_kind` breakdown.
- `ticket_metrics()` — status/priority/classification distributions, average resolution hours.
- `knowledge_growth()` — docs/chunks added per day, by source type.
- `agent_performance()` — flow outcomes (completed / awaiting / rejected / failed) per flow key
  and engine distribution.
- `overview()` — the whole page in one payload (single round-trip).

## 4. Public widget

Owners enable the widget from the API (`/widget/enable`), which stores a
`secrets.token_urlsafe(32)` token on the workspace settings. Public endpoints:

- `POST /api/v1/public/{slug}/chat` — `X-Widget-Token` header, `{message}` → `ChatResponse`.
  Consumes the tenant's request quota and returns a grounded answer or a handoff suggestion.
- `POST /api/v1/public/{slug}/tickets` — lets end users raise a human ticket from the widget.

The token is scoped to one workspace and can be rotated or revoked at any time; enabling a new
widget regenerates the token. Frontend exposes the token to owners via the workspace settings
API so a site embed can be generated (see the Docs page).

## 5. Migration

```bash
cd apps/backend && .venv/bin/alembic upgrade head   # applies 0002 (jobs table)
```

## 6. Tests (`tests/test_volume4.py`)

7 new pytest cases cover: billing summary shape, plan change + permission, analytics overview
shape, job creation/execution, document re-indexing, widget chat flow, and usage metering kinds.
Full suite: **44 passing** (45 with the CrewAI smoke test on Python 3.12).
