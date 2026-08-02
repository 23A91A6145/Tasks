# Phase 1.1 — Architecture

```
                        ┌────────────────────────────┐
                        │   Browser (Next.js 15)     │
                        │  Landing · Auth · Dashboard│
                        └──────────────┬─────────────┘
                                       │ REST + JSON (Bearer JWT)
                                       ▼
                        ┌────────────────────────────┐
                        │   FastAPI (API Gateway)    │
                        │  /api/v1/auth  /workspaces │
                        │  /admin  /health  /docs    │
                        └──────────────┬─────────────┘
                                       │
                ┌──────────────────────┼───────────────────────┐
                ▼                      ▼                       ▼
        auth_service             workspace_service         audit service
        (JWT + bcrypt)           (tenancy + RBAC)          (activity log)
                │                      │                       │
                └──────────────────────┼───────────────────────┘
                                       ▼
                        ┌────────────────────────────┐
                        │  PostgreSQL / SQLite        │
                        │  users · organizations      │
                        │  memberships · activity_logs│
                        └────────────────────────────┘
```

## Multi-tenancy strategy
- **Shared database, row-level tenancy.** Every tenant-scoped row references `organization_id`.
- The API resolves tenancy from the URL `slug` (`/api/v1/workspaces/{slug}/...`) and always
  verifies an **active membership** before touching data.
- No tenant ID is ever trusted from the client alone — it must be proven by membership.

## Auth model
- `access_token` (30 min) + `refresh_token` (30 days), both signed `HS256` JWT.
- Passwords hashed with bcrypt (12 rounds).
- Endpoints are role-gated through FastAPI dependencies.

## Layering (backend)
```
app/main.py          → app factory, CORS, lifespan, routers
app/api/v1/*         → HTTP layer (routers + dependency injection)
app/services/*       → business logic (auth, workspace, audit)
app/models/*         → SQLAlchemy 2.0 ORM models
app/schemas/*        → pydantic v2 request/response contracts
app/core/*           → config, db engine, security, permissions
```

## Frontend structure
```
app/(auth)   → login / register (client)
app/(app)    → protected dashboard shell + pages (client)
app/         → landing page (server, static marketing)
components/  → ui kit + layout + feature components
lib/         → api client, session context, utils
```
