"""Role definitions and permission helpers (RBAC)."""

ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_AGENT = "agent"
ROLE_USER = "user"

VALID_ROLES = (ROLE_OWNER, ROLE_ADMIN, ROLE_MANAGER, ROLE_AGENT, ROLE_USER)

ROLE_HIERARCHY = (ROLE_USER, ROLE_AGENT, ROLE_MANAGER, ROLE_ADMIN, ROLE_OWNER)
ROLE_RANK = {role: i for i, role in enumerate(ROLE_HIERARCHY)}


def can(actor_role: str, required_role: str) -> bool:
    """True if actor_role is at least required_role in the hierarchy."""
    return ROLE_RANK.get(actor_role, -1) >= ROLE_RANK.get(required_role, 99)
