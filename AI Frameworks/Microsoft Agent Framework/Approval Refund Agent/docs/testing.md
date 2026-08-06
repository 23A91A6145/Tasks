# 🧪 Testing Report

All tests are pure offline unit/integration tests (no LLM, no network). Run with:

```bash
python -m pytest -q        # or: make test
```

Current status: **36 passed** (`tests/`, pytest 9.x).

## Coverage Map (Phase 4.5)

| # | Test case | Where | Status |
|---|---|---|---|
| 1 | Valid refund → approval_required + checkpoint saved | `test_workflow.py` | ✅ |
| 2 | Invalid refund: unknown customer | `test_workflow.py` | ✅ |
| 3 | Invalid refund: amount exceeds order total | `test_workflow.py` | ✅ |
| 4 | Invalid refund: malformed / missing IDs | `test_workflow.py` | ✅ |
| 5 | Duplicate request blocked (active ticket) | `test_agent.py` | ✅ |
| 6 | Double-approve blocked (single-spend token) | `test_workflow.py` | ✅ |
| 7 | Reject flow → Rejected + checkpoint purged + notification | `test_workflow.py` | ✅ |
| 8 | Approve flow → Approved + payment executed + audit | `test_workflow.py` | ✅ |
| 9 | SLA timeout → Expired + checkpoint purged | `test_workflow.py` | ✅ |
| 10 | Large amount refund → Manager gate enforced | `test_workflow.py` | ✅ |
| 11 | Unauthorized reviewer → PermissionError / HTTP 403 | `test_workflow.py`, `test_api.py` | ✅ |
| 12 | Hold → resume works after Hold | `test_workflow.py` | ✅ |
| 13 | Escalate → role promoted to Manager | `test_workflow.py` | ✅ |
| 14 | Request More Info transition | `test_workflow.py` | ✅ |
| 15 | Auto-approval path (≤ $50, Low risk) | `test_agent.py` | ✅ |
| 16 | Policy engine edge cases (0/negative amounts, ceiling) | `test_workflow.py` | ✅ |
| 17 | Payment tool safety invariants | `test_workflow.py` | ✅ |
| 18 | Input validation via Pydantic models | `test_models.py` | ✅ |
| 19 | Dashboard statistics correctness | `test_workflow.py` | ✅ |
| 20 | API: health, info, stats, dashboard render | `test_api.py` | ✅ |
| 21 | API: chat → approval → decision → notification outbox | `test_api.py` | ✅ |
| 22 | API: 403, 404, 422 error contracts | `test_api.py` | ✅ |

## Manual / E2E Verification

```bash
python run_demo.py        # 6 scenarios: auto-approve, pause, duplicate, RBAC, resume, SLA expiry
python main.py            # DevUI at http://127.0.0.1:8000
```

Manual happy path:

1. Open `http://127.0.0.1:8000`.
2. In the chat, send `Process a refund of $125 for customer CUST-1045 order ORD-5582 due to wrong item`.
3. The ticket appears in **Pending Queue**; switch reviewer to *Bob Johnson (Manager)*.
4. Click **Approve** → refund executes, status flips to Approved, a customer email preview appears.
5. Inspect `logs/audit.log` and the notification outbox.
