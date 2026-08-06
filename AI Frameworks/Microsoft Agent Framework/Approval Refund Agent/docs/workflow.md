# 🔄 Approval-Gated Refund Agent Workflow Flow

This document details the step-by-step sequence of events for a refund transaction, including state transitions, checkpointing, and execution resumption.

## 🏃 Workflow Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Customer / CSR
    participant Agent as AI Safety Agent
    participant Policy as Policy Engine
    participant Checkpoint as Checkpoint Store
    participant DB as Approvals Database
    actor Reviewer as Human Reviewer
    participant Gateway as Payment Gateway
    participant Audit as Audit Log

    Customer->>Agent: "Refund $125 for order ORD-5582 due to broken CPU kit"
    Agent->>Agent: Parse customer_id, order_id, amount, reason
    Agent->>Policy: Validate policy (customer matching, amount limit)
    alt Policy Invalid
        Policy-->>Agent: Fail (e.g. amount exceeds order total)
        Agent-->>Customer: Return "Refund Rejected: Policy violation"
    else Policy Valid
        Policy-->>Agent: Success (Requires Reviewer or Manager role)
    end

    Agent->>Agent: Detect execute_payment_refund requires approval
    Agent->>Checkpoint: Save workflow context (args, call stack)
    Checkpoint-->>Agent: Saved checkpoint on disk
    Agent->>DB: Save approval ticket (Status: "Pending")
    Agent-->>Customer: Return "Refund request REQ-XXXX created, pending human review"

    Note over Reviewer, DB: Human-in-the-Loop Intermission
    Reviewer->>DB: View pending approvals on DevUI
    Reviewer->>DB: Submit Decision (Approve / Reject, Notes, Role)
    
    alt RBAC Fails
        DB-->>Reviewer: Error: "Standard Reviewer cannot approve Manager limit"
    else RBAC Passes
        DB->>Checkpoint: Load checkpoint context
        Checkpoint-->>DB: Retreive tool call & arguments
        
        alt Action == Approve
            DB->>Gateway: Execute refund payment (transaction logic)
            Gateway-->>DB: Gateway receipt (transaction ID)
            DB->>Checkpoint: Clean up checkpoint file (remove spend token)
            DB->>DB: Update ticket status to "Approved"
            DB->>Audit: Write secure transaction logs to audit.log
        else Action == Reject
            DB->>Checkpoint: Clean up checkpoint file
            DB->>DB: Update ticket status to "Rejected"
            DB->>Audit: Write cancellation logs to audit.log
        end
        
        DB-->>Reviewer: Return final decision result & notification template
    end
```

---

## 🚦 State Transition Matrix

The approval request transitions through the following lifecycle states:

| Source State | Trigger / Action | Target State | Checkpoint Action | Description |
|---|---|---|---|---|
| **None** | Customer Request | **Pending** | Saved | The request is verified, a refund tool call is prepared, and a checkpoint is written. |
| **Pending** | `Hold` by Reviewer | **Hold** | Maintained | The ticket is paused. Reviewer can write notes asking for more information. |
| **Pending** / **Hold** | `Escalate` by Reviewer | **Escalated** | Maintained | The required authorization role is upgraded from `Reviewer` to `Manager`. |
| **Pending** / **Escalated** | `Approve` by authorized Role | **Approved** | Deleted | The checkpoint is loaded, the payment executes, and the checkpoint is purged to prevent reuse. |
| **Pending** / **Escalated** | `Reject` by Reviewer | **Rejected** | Deleted | The transaction is cancelled, and the checkpoint is purged. |
| **Pending** | `Request More Info` | **Request More Info** | Maintained | The ticket remains active, waiting for client response. |
