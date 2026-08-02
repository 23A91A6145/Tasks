# Phase 1.1 — Feature Matrix (Volume 1)

| Feature | Status | Where |
|---|---|---|
| Register (user + optional workspace) | ✅ V1 | `POST /api/v1/auth/register` |
| Login / Refresh / Logout | ✅ V1 | `POST /api/v1/auth/{login,refresh,logout}` |
| Current user + memberships | ✅ V1 | `GET /api/v1/auth/me` |
| Create / List workspaces | ✅ V1 | `POST/GET /api/v1/workspaces` |
| Workspace detail / update / delete | ✅ V1 | `/workspaces/{slug}` |
| Invite member by email | ✅ V1 | `POST /workspaces/{slug}/members` |
| Change role / remove member | ✅ V1 | `PATCH/DELETE /workspaces/{slug}/members/{user_id}` |
| Activity feed | ✅ V1 | `GET /workspaces/{slug}/activity` |
| Workspace stats (dashboard KPIs) | ✅ V1 | `GET /workspaces/{slug}/stats` |
| Super admin overview | ✅ V1 | `GET /api/v1/admin/overview` |
| OpenAPI / Swagger UI | ✅ V1 | `/docs` |
| Health check | ✅ V1 | `/health` |
| Landing + auth + dashboard UI | ✅ V1 | Next.js app |
| RBAC enforcement | ✅ V1 | FastAPI dependencies |
| Tenant isolation (403 on foreign slug) | ✅ V1 | membership check |

## Later volumes (placeholders in UI today)
| Feature | Volume |
|---|---|
| CrewAI hierarchical crew | V2 |
| CrewAI flows + checkpoints | V2 |
| Knowledge upload + search | V2–V3 |
| RAG pipeline (Qdrant) | V3 |
| MCP servers | V3 |
| Usage limits & plans | V4 |
| Analytics dashboards | V4 |
| Deployment (free tiers) | V5 |
