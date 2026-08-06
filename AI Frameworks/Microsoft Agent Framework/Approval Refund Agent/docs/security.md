# 🔐 Security & Error Handling

Everything in Phase 4 (Production & Security) implemented and explained.

## Input Validation (`app/models.py`, `app/refund_tool.py`)

- Pydantic models enforce strict formats:
  - `Customer ID` must match `CUST-\d+`, `Order ID` must match `ORD-\d+`.
  - `amount > 0` and `amount <= MAX_REFUND_CEILING` ($1,000,000).
  - Decision `action` restricted to `Approve | Reject | Hold | Escalate | Request More Info`.
  - `reviewer_role` restricted to `Reviewer | Manager`; `reviewer_name` non-empty.
- Structural checks run *before* the policy engine, so malformed payloads are rejected
  at the boundary (HTTP 422 via the validation exception handler).

## Role-Based Access Control (RBAC)

| Ticket classification | Approver required |
|---|---|
| Amount < `MANAGER_LIMIT` and customer risk is Low/Medium | Standard Reviewer |
| Amount ≥ `MANAGER_LIMIT` **or** customer risk is High | Manager |
| Any ticket after an `Escalate` action | Manager |

A Standard Reviewer approving a Manager-only ticket is logged as a security alert in
`logs/errors.log` and answered with `403 Forbidden`.

## Rate Limiting (`app/middleware.py`)

- Per-IP sliding window: `RATE_LIMIT_PER_MINUTE` (default 120) requests per 60 seconds.
- Excess requests receive `429 Too Many Requests`.
- Static/favicon paths are exempt to avoid UI jitter.

## Human-in-the-Loop Enforcement

- The payment tool is registered as `@tool(approval_mode="always_require")` through the
  real Microsoft Agent Framework (`agent-framework-core`). If the package is absent the
  app degrades to an equivalent local decorator so the project still runs offline.
- Auto-approval is a narrow, explicit carve-out: amount ≤ `MAX_AUTO_APPROVE_AMOUNT`,
  customer risk `Low`, account `Active`. Everything else **must** pass the human gate.

## Audit Logging (`logs/audit.log`)

Append-only JSON Lines; each final decision records:

```json
{"timestamp": "...", "request_id": "REF-...", "customer_id": "CUST-...",
 "order_id": "ORD-...", "amount": 125.0, "decision": "Approved",
 "reason": "...", "reviewer": "Bob Johnson", "reviewer_role": "Manager",
 "notes": "...", "ip_address": "127.0.0.1", "session_id": "SESSION-..."}
```

## Environment Variable Hygiene

- All secrets/config live in `.env` (git-ignored); `.env.example` documents each key.
- `GROQ_API_KEY` is never logged; empty keys cause a graceful fallback to the parser.

## Error Handling (`main.py`)

| Scenario | Behaviour |
|---|---|
| Missing/invalid fields in chat | `clarification_required` response with missing-field map |
| Unknown customer / bad order / over-amount | `policy_rejected` with the exact policy reason |
| Duplicate active ticket | `policy_rejected` anti-fraud block |
| Reviewer unauthorized | `403 Forbidden` (PermissionError) |
| Request not found / invalid ID | `404 Not Found` |
| Invalid decision body | `422 Validation Error` |
| Missing checkpoint on decision | `409 Workflow State Missing` (FileNotFoundError) |
| Unhandled exceptions | Global `500` handler that writes to `logs/errors.log` |

## Testing Security Cases

See `docs/testing.md` for the covered matrix, including unauthorized reviewer,
double-approve, duplicate claim, timeout recovery, and large-amount refunds.
