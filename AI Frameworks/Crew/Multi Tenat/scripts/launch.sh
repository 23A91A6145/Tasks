#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
#  THE ONE COMMAND — TenantDesk AI, everything, all aspects.
#
#  Provisions (venv + deps + .env) → seeds demo tenants → creates a platform
#  super admin → runs the full test/typecheck gate → starts backend + frontend.
#
#  Usage:
#    bash scripts/launch.sh
#    SUPER_ADMIN_EMAIL=you@example.com SUPER_ADMIN_PASSWORD=secret bash scripts/launch.sh
#    SKIP_TESTS=1 bash scripts/launch.sh          # skip the verification gate
#    bash scripts/launch.sh --tests-only          # run the whole gate, start nothing
#    bash scripts/launch.sh --docker              # build & run the Docker Compose stack
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TESTS_ONLY=0
DOCKER=0
for arg in "$@"; do
  case "$arg" in
    --tests-only) TESTS_ONLY=1 ;;
    --docker)     DOCKER=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

SUPER_ADMIN_EMAIL="${SUPER_ADMIN_EMAIL:-admin@platform.io}"

step()  { printf "\n\033[1;36m▸ %s\033[0m\n" "$*"; }
ok()    { printf "\033[1;32m  ✓ %s\033[0m\n" "$*"; }
warn()  { printf "\033[1;33m  ! %s\033[0m\n" "$*"; }

# ── Docker mode ────────────────────────────────────────────────────────────
if [ "$DOCKER" -eq 1 ]; then
  step "Docker Compose: building the full stack (db + backend + worker + frontend)"
  docker compose up --build -d
  step "Waiting for the API to come up on :8000"
  API_UP=0
  for _ in $(seq 1 30); do
    if curl -sf http://localhost:8000/health >/dev/null 2>&1; then API_UP=1; break; fi
    sleep 2
  done
  if [ "$API_UP" -eq 0 ]; then
    echo "API did not become healthy — check: docker compose logs backend" >&2
    exit 1
  fi

  PGHOST_URL="postgresql+psycopg2://tenantdesk:tenantdesk@localhost:5432/tenantdesk"
  step "Seeding demo data (Acme Support + Globex Helpdesk) into the Docker Postgres"
  DATABASE_URL="$PGHOST_URL" "$ROOT/apps/backend/.venv/bin/python" "$ROOT/scripts/seed.py"
  step "Super admin: ${SUPER_ADMIN_EMAIL}"
  ( cd "$ROOT/apps/backend" && DATABASE_URL="$PGHOST_URL" .venv/bin/python -m scripts.create_superadmin \
    "$SUPER_ADMIN_EMAIL" ${SUPER_ADMIN_PASSWORD:+--password "$SUPER_ADMIN_PASSWORD"} )

  docker compose ps
  ok "Stack up. Frontend http://localhost:3000 · API docs http://localhost:8000/docs"
  echo "   Demo logins (password: demo-password-123): owner@demo.com · admin@demo.com · agent@demo.com · user@demo.com · owner2@demo.com"
  echo "   One-click demo: POST /api/v1/auth/demo (or the homepage button) — no account needed"
  echo "   Super admin: ${SUPER_ADMIN_EMAIL} → /admin"
  exit 0
fi

# ── 1. Provision (idempotent) ──────────────────────────────────────────────
step "1/4 Provision: venv, deps, .env"
NEED_SETUP=0
[ -d "$ROOT/apps/backend/.venv" ]          || NEED_SETUP=1
[ -d "$ROOT/apps/frontend/node_modules" ]  || NEED_SETUP=1
if [ "$NEED_SETUP" -eq 1 ]; then
  bash "$ROOT/scripts/setup.sh"
else
  ok "venv + node_modules already present — skipping setup"
fi

# ── 2. Seed demo tenants (idempotent) ──────────────────────────────────────
step "2/4 Seed demo data (Acme Support + Globex Helpdesk)"
"$ROOT/apps/backend/.venv/bin/python" "$ROOT/scripts/seed.py"

# ── 3. Platform super admin ────────────────────────────────────────────────
step "3/4 Super admin: ${SUPER_ADMIN_EMAIL}"
# run from apps/backend so `-m scripts.create_superadmin` resolves the package
if [ -n "${SUPER_ADMIN_PASSWORD:-}" ]; then
  ( cd "$ROOT/apps/backend" && .venv/bin/python -m scripts.create_superadmin \
    "$SUPER_ADMIN_EMAIL" --password "$SUPER_ADMIN_PASSWORD" )
  ok "super admin ready — log in and open /admin"
else
  ( cd "$ROOT/apps/backend" && .venv/bin/python -m scripts.create_superadmin "$SUPER_ADMIN_EMAIL" )
  ok "if a password was printed above, write it down — it is shown once."
fi

# ── 4. Verification gate ───────────────────────────────────────────────────
step "4/4 Verification gate (tests + typecheck + build check)"
if [ "${SKIP_TESTS:-0}" != "1" ]; then
  ( cd "$ROOT/apps/backend" && .venv/bin/pytest -q ) || { echo "tests failed" >&2; exit 1; }
  ( cd "$ROOT/apps/frontend" && npx tsc --noEmit )    || { echo "tsc failed" >&2; exit 1; }
  ok "backend test suite + tsc --noEmit all green"
else
  warn "SKIP_TESTS=1 — skipping verification gate"
fi

if [ "$TESTS_ONLY" -eq 1 ]; then
  ok "Everything is in order. Run the app with:  bash scripts/launch.sh"
  exit 0
fi

# ── Start everything ───────────────────────────────────────────────────────
step "Starting TenantDesk AI"
cat <<EOF

─────────────────────────────────────────────────────────────────
  TenantDesk AI  —  http://localhost:3000     (Frontend)
  API docs       —  http://localhost:8000/docs
  Health         —  http://localhost:8000/health

  Demo logins (from seed)        password: demo-password-123
    owner@demo.com   · Acme Support  (owner, all access)
    admin@demo.com   · Acme Support  (admin)
    agent@demo.com   · Acme Support  (agent)
    user@demo.com    · Acme Support  (end user)
    owner2@demo.com  · Globex Helpdesk (second tenant)

  One-click demo — no account needed
    Homepage "Open live demo" button or POST /api/v1/auth/demo
    → provisions the shared demo workspace on first use

  Super admin (platform console)  ${SUPER_ADMIN_EMAIL}
    → open /admin once logged in

  Widget demo     — http://localhost:3000/widget-demo
─────────────────────────────────────────────────────────────────
  Press Ctrl+C to stop both servers.
EOF

bash "$ROOT/scripts/dev.sh"
