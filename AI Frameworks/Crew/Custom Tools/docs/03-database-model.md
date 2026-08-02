# Phase 1.1 — Database Model

## users
| column | type | notes |
|---|---|---|
| id | uuid(str) | PK |
| email | varchar(320) | unique, indexed |
| password_hash | varchar(255) | bcrypt |
| full_name | varchar(120) | |
| avatar_url | varchar(500) | nullable |
| is_super_admin | bool | platform operator |
| is_active | bool | soft disable |
| last_login_at | datetime | |
| created_at / updated_at | datetime | |

## organizations (workspaces / tenants)
| column | type | notes |
|---|---|---|
| id | uuid(str) | PK |
| name | varchar(120) | |
| slug | varchar(120) | unique, URL-safe |
| description | text | nullable |
| plan | varchar(20) | default `free` |
| settings | json | tenant config blob |
| created_at / updated_at | datetime | |

## memberships (user ↔ organization)
| column | type | notes |
|---|---|---|
| id | uuid(str) | PK |
| organization_id | uuid | FK → organizations |
| user_id | uuid | FK → users |
| role | varchar(20) | owner/admin/manager/agent/user |
| status | varchar(20) | active (pending reserved) |
| created_at | datetime | |
| **unique** | (organization_id, user_id) | no duplicates |

## activity_logs (audit trail)
| column | type | notes |
|---|---|---|
| id | uuid(str) | PK |
| organization_id | uuid | FK, nullable |
| user_id | uuid | FK, nullable |
| action | varchar(120) | e.g. `member.invited` |
| entity_type / entity_id | varchar | nullable |
| metadata_json | json | extra detail |
| created_at | datetime | |

## Relationship rules
- user 1—N memberships N—1 organization
- Deleting an organization cascades memberships + activity logs.
- Deleting a user cascades their memberships (their activity log rows keep user_id nulled-safe via nullable FK).
