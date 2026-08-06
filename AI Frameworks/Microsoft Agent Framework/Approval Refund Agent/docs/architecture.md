# 🏛️ Approval-Gated Refund Agent — System Architecture

An AI-powered Refund Management System with **Human-in-the-Loop (HITL)** safety controls,
built on the Microsoft Agent Framework (MAF) approval semantics.

## 🎯 Aim & Purpose

Financial operations like issuing customer refunds carry significant risk. Letting an
AI agent execute payments autonomously creates risks of duplicate payments, compliance
violations, and security exploits.

The aim is a **HITL architecture** where:

1. An AI Agent parses and validates refund requests.
2. Sensitive tools (payment execution) are intercepted via an **approval gate**.
3. The workflow state is persisted as a **checkpoint** on disk.
4. A human reviewer approves/rejects from the **DevUI dashboard**.
5. On approval, the workflow resumes and the payment executes.
6. A tamper-resistant **audit trail** is recorded and notifications are generated.

## 🧩 Component Diagram

```mermaid
graph TD
    Customer[Customer Request] -->|Natural Language| Agent[AI Refund Agent]
    Agent -->|1. Parse details| Parser[Regex / LLM Parser (Groq / Ollama)]
    Agent -->|2. Verify policy| Policy[Policy Validation Engine]
    Policy -->|Failed| RejectMsg[Policy Rejection Message]
    Policy -->|Passed| AutoCheck{Micro-refund & Low risk?}
    AutoCheck -->|Yes ≤ MAX_AUTO_APPROVE| AutoExec[Execute Payment Tool]
    AutoExec --> Audit[Audit Log]
    AutoCheck -->|No| ToolGate{Sensitive Tool Gate
        approval_mode='always_require'}
    ToolGate -->|Pause & serialize| Checkpoint[Checkpoint Store]
    Checkpoint -->|Create ticket| DB[Approvals Database]
    DB -->|Render| DevUI[Compliance DevUI Portal]
    Reviewer[Human Reviewer] -->|Approve / Reject / Hold / Escalate| DevUI
    DevUI -->|Decision + RBAC| ApprovalHandler[Approval Service]
    ApprovalHandler --> RBAC{Authorized role?}
    RBAC -->|Blocked| Forbidden[403 Forbidden]
    RBAC -->|Approved| Resume[Load Checkpoint & Resume]
    Resume -->|3. Execute payment| PayTool[Payment Execution Tool]
    PayTool -->|Gateway receipt| Audit[Audit Log + SLA cleanup]
    Audit -->|Notify| Outbox[Notification Outbox / Email Templates]
```

## 🏗️ Layered Modules

| Module | Responsibility |
|---|---|
| `app/settings.py` | Single source of truth for all configuration (`.env`). |
| `app/config.py` | Backward-compatible re-exports for existing imports. |
| `app/agent.py` | Conversational agent: LLM-aware parser (Groq/Ollama) with deterministic regex fallback, policy routing, auto-approval eligibility, checkpoint creation, duplicate-claim protection. |
| `app/refund_tool.py` | Sensitive payment tool registered via the real MAF `@tool(approval_mode="always_require")`; input validation; policy engine; auto-approval eligibility. |
| `app/workflow.py` | Checkpoint save / load / delete state machine (pause & resume). |
| `app/approval.py` | Approval request DB, SLA lease expiry, RBAC, decision handling, tool execution on approve, checkpoint purge. |
| `app/models.py` | Pydantic schemas with strict input validation (IDs, amounts, actions, roles). |
| `app/services.py` | Dashboard statistics, email/internal notification templates, persisted notification outbox. |
| `app/middleware.py` | Per-IP rate limiting. |
| `main.py` | FastAPI app: REST API, exception handlers, DevUI HTML, seed/reset endpoint. |
| `templates/dashboard.html` | Glassmorphism DevUI: stats, chat console, approval queue, detail pane, timeline, logs, inbox. |

## 🛡️ Safety Invariants

- **Never execute without approval**: the payment tool carries `approval_mode="always_require"`.
- **Single-spend token**: the checkpoint is deleted the moment a decision finalizes the request, so the same ticket can never double-execute.
- **RBAC**: Manager-only tickets reject Standard Reviewer approvals with HTTP 403.
- **Duplicate-claim block**: only one *active* ticket per order; resubmissions are rejected.
- **SLA lease**: pending tickets auto-expire after the configured timeout and their checkpoints are purged.
- **Audit immutability**: every final decision is appended to `logs/audit.log` as JSON lines (timestamp, reviewer, role, IP, session, notes).
