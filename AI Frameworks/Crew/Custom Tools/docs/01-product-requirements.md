# Phase 1.1 — Product Requirements (PRD)

## 1. Target users
- **SMB support teams** wanting an AI-first helpdesk.
- **Companies** wanting an internal Copilot over their docs.
- **Developers/agencies** white-labeling support AI to clients.
- **Students/self-hosters** running the same stack on a laptop.

## 2. Personas & roles (RBAC hierarchy)
```
Super Admin       → platform operator (see all workspaces)
Tenant Admin/Owner→ owns workspace, manages members & settings
Support Manager   → manages agents/tickets/flows (Vol. 2+)
Support Agent     → triages & resolves tickets (Vol. 2+)
End User          → chats with the AI assistant
```
Volume 1 implements: `owner`, `admin`, `manager`, `agent`, `user` + platform `super_admin`.

## 3. Functional requirements (Volume 1 scope)
- **FR-1 Auth:** register, login, refresh, logout, "me".
- **FR-2 Workspaces:** create, list, view, update, delete (owner), slug routing.
- **FR-3 Membership:** invite by email, change role, remove member, role rules.
- **FR-4 Isolation:** user A can never read/modify user B's workspace.
- **FR-5 Audit:** every workspace-scoped action is logged and visible.
- **FR-6 Admin:** super admin overview endpoint.
- **FR-7 UI:** landing, login, register, dashboard shell, dashboard, users, settings, billing placeholders.

## 4. Non-functional requirements
- **Security:** bcrypt, JWT expiry, no secrets in repo, CORS scoped to frontend.
- **Portability:** SQLite on laptop, Postgres in Docker, same code.
- **Accessibility:** keyboard navigable, semantic HTML, contrast-compliant, focus rings.
- **Polish:** light/dark themes, responsive, loading states, empty states, toasts.

## 5. Out of scope (later volumes)
CrewAI agents, flows, RAG/knowledge, MCP, usage metering, billing, monitoring.

## 6. Success criteria (Volume 1)
- A new user registers, creates a workspace, invites a teammate, and sees the dashboard.
- Teammate cannot access another workspace (403).
- Owner can demote/promote/remove members; roles are enforced on every endpoint.
- All actions appear in the activity feed.
- `pytest` green, `next build` green, Docker Compose brings the whole stack up.
