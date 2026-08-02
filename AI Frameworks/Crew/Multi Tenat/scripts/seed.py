"""Seed demo data: users, workspaces, members + the shared demo workspace.

Usage (from repo root, backend venv active):
    apps/backend/.venv/bin/python scripts/seed.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "apps" / "backend"))

from sqlalchemy import select  # noqa: E402

from app.core.database import SessionLocal, init_db  # noqa: E402
from app.core.permissions import ROLE_ADMIN, ROLE_AGENT, ROLE_MANAGER, ROLE_OWNER, ROLE_USER  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import Membership, Organization, User  # noqa: E402
from app.services import audit  # noqa: E402
from app.services.demo import DEMO_EMAIL, DEMO_PASSWORD, ensure_demo  # noqa: E402
from app.services.workspace_service import unique_slug  # noqa: E402

DEMO = [
    {
        "email": "admin@demo.com",
        "full_name": "Bella Admin",
        "workspace": "Acme Support",
        "role": ROLE_ADMIN,
    },
    {
        "email": "manager@demo.com",
        "full_name": "Chris Manager",
        "workspace": "Acme Support",
        "role": ROLE_MANAGER,
    },
    {
        "email": "agent@demo.com",
        "full_name": "Dana Agent",
        "workspace": "Acme Support",
        "role": ROLE_AGENT,
    },
    {
        "email": "user@demo.com",
        "full_name": "Sam User",
        "workspace": "Acme Support",
        "role": ROLE_USER,
    },
    {
        "email": "owner2@demo.com",
        "full_name": "Pat Second",
        "workspace": "Globex Helpdesk",
        "role": ROLE_OWNER,
    },
]


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        for item in DEMO:
            user = db.execute(select(User).where(User.email == item["email"])).scalar_one_or_none()
            if user is None:
                user = User(
                    email=item["email"],
                    password_hash=hash_password(DEMO_PASSWORD),
                    full_name=item["full_name"],
                )
                db.add(user)
                db.flush()
                print(f"  + user {item['email']}")
            else:
                user.password_hash = hash_password(DEMO_PASSWORD)

            org = db.execute(
                select(Organization).where(Organization.name == item["workspace"])
            ).scalar_one_or_none()
            if org is None:
                slug = unique_slug(db, item["workspace"])
                org = Organization(name=item["workspace"], slug=slug)
                db.add(org)
                db.flush()
                print(f"  + workspace {item['workspace']} (/{slug})")

            exists = db.execute(
                select(Membership).where(
                    Membership.organization_id == org.id, Membership.user_id == user.id
                )
            ).scalar_one_or_none()
            if exists is None:
                db.add(Membership(organization_id=org.id, user_id=user.id, role=item["role"]))
                audit.log_activity(
                    db,
                    organization_id=org.id,
                    user_id=user.id,
                    action="member.invited",
                    entity_type="user",
                    entity_id=user.id,
                    metadata={"email": user.email, "role": item["role"]},
                )

        owner = ensure_demo(db)
        print(f"  + demo workspace ready (owner: {owner.email})")

        db.commit()
        print("\n✅ Seed complete.")
        print("   One-click demo:  POST /api/v1/auth/demo  (no account needed)")
        print(f"   Or log in with {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print("   Other demo users: admin@demo.com / manager@demo.com / agent@demo.com / user@demo.com")
        print("   Tip: open a ticket in the UI and press 'AI handle' to run the crew flow.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
