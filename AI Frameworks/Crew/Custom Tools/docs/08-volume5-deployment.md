# Volume 5 — Product Polish, Free-Tier Deployment & Portfolio Docs

**Goal:** the platform is feature-complete; this volume makes it a credible, deployable SaaS
you can point at on a free tier and hand over as a portfolio artifact.

## What changed

### Product polish (frontend)

- **Real Analytics page** (`/app/analytics`) — replaces the placeholder. KPI cards (requests,
  budget %, tokens, cost), a 30-day request bar chart, type/status/priority/source breakdowns,
  average resolution time, workflow performance table and engine distribution. All driven by
  `/analytics/overview` in a single round-trip.
- **Real Billing page** (`/app/billing`) — current plan header, billing period, live usage
  meters (color-coded at 70%/90% thresholds), and the full plan catalog with one-click switching
  (owner-only, guarded by role on the backend too).
- **Jobs page** (`/app/jobs`) — list with progress bars and status badges, job creation modal
  (re-index a picked document, crawl a URL, import an FAQ, generate a weekly report), retry of
  failed jobs and delete. New sidebar entry.
- **Fixed the ticket resume bug** — approve/reject now calls
  `POST /flows/{run_id}/resume` (`{approved: true|false}`), the endpoint that actually exists,
  then re-fetches the ticket. Previously it called a non-existent `/tickets/{id}/resume`.
- **Public site** — dedicated `/features`, `/pricing` and `/docs` pages (navbar now routes to
  them) plus a shared footer. Docs page covers architecture, quick start, auth, the public
  widget embed, jobs/billing and deployment.
- Production `next build` passes for all routes.

### Jobs worker

- `JOBS_INLINE` env switch: `1` (default) runs jobs inline, `0` leaves them queued for a
  background worker. `python -m scripts.worker` polls the `jobs` table; the same
  checkpoint/retry semantics apply. Drop-in compatible with Redis/Celery later.

### Docker Compose (free-tier friendly)

- Backend now runs `alembic upgrade head` before `uvicorn` (no manual migrations).
- Named `storage` volume for uploaded documents + vector store.
- Job `worker` service (DB-backed, checkpointed) starts with the stack by default.
- Optional Qdrant commented out with instructions; the app still works fully offline with the
  built-in hash embeddings.

## Deployment options

### 1. Render (all free)

- **Postgres**: create a free Postgres instance; copy the internal URL.
- **API**: new Web Service → root `apps/backend` → start `alembic upgrade head && uvicorn
  app.main:app --host 0.0.0.0 --port 10000` → set `DATABASE_URL`, `SECRET_KEY`, `STORAGE_DIR`.
- **Web**: new Static Site / Next.js build → root `apps/frontend` → `NEXT_PUBLIC_API_URL` =
  your Render API URL. Frontend needs a running server for API calls, so a Node Web Service
  (`npm run build && npm start`) is the pragmatic choice.
- (Optional) a `worker` Web Service running `python -m scripts.worker` with `JOBS_INLINE=0`.

### 2. Fly.io

```bash
cd apps/backend && fly launch   # set DATABASE_URL, SECRET_KEY; fly postgres create
cd apps/frontend && fly launch  # set NEXT_PUBLIC_API_URL to the API app URL
```

### 3. Railway / Supabase + Vercel

- Railway for the API (attach a Postgres plugin), Vercel for the frontend with
  `NEXT_PUBLIC_API_URL` set to the Railway URL.

### 4. Docker Compose (self-host)

```bash
docker compose up --build                       # api + web + postgres
docker compose up --build      # db + backend + worker + frontend
```

## Security checklist (production)

- Set a strong `SECRET_KEY` and rotate it in CI/CD.
- Enable HTTPS at the proxy; set `BACKEND_CORS_ORIGINS` to your exact domain.
- Use Postgres (not the default SQLite) — the compose file wires it up.
- Keep the AI engine on the free `fallback` engine until you add an LLM key; add keys behind an
  env var, never in the repo.
- Widget tokens are per-workspace secrets — rotate them on suspected leak.

## Verification

```bash
cd apps/backend && .venv/bin/pytest -q            # 44 passing
cd apps/frontend && npm run typecheck && npm run build
docker compose config                             # validate the compose file
```

## Deliverables recap

| Artifact | Where |
|---|---|
| Product docs site | `/apps/frontend/app/{features,pricing,docs}/page.tsx` |
| API reference + widget embed | README + Docs page |
| Deployment guides | this doc + `docker-compose.yml` |
| Volume 4 spec | `docs/07-volume4-monetization.md` |
| Architecture notes | `docs/02-architecture.md` |
| Tests | `apps/backend/tests/test_volume4.py` (44 total) |
