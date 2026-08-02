# Apps/Admin — Platform Admin Console

**Status: implemented in-app (Volume 5).**

Platform-level admin for `super_admin` users is served by:

- **Frontend** — a dedicated in-app console at `/admin` (overview KPIs, plan catalog) and
  `/admin/workspaces` (all tenants + plans + member counts). The link only appears in the
  sidebar for super admins, and the route is guarded client-side.
- **Backend** — `GET /api/v1/admin/overview` and `GET /api/v1/admin/workspaces`, both gated by
  `get_current_super_admin` (`app/api/deps.py`).

Make a user a super admin:

```bash
cd apps/backend && .venv/bin/python -m scripts.create_superadmin you@example.com [--password secret]
```

The `User.is_super_admin` boolean is the source of truth; the guard returns 403 for everyone else.
