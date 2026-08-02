# Volume 2 — AI Support: Knowledge, Crew & Checkpointed Flows

**Goal:** every tenant gets a real AI support crew — hierarchical CrewAI agents that triage
tickets, retrieve answers from an isolated per-tenant knowledge base, draft grounded replies,
and pause at a human checkpoint when a real person must approve (or reject) the AI's decision.
Runs on a laptop with **zero API keys**.

## Decision 1 — The AI engine ladder (`AI_ENGINE=auto`)

One facade (`app/agents/engine.py`) picks the best engine at runtime:

| Priority | Engine | When selected | Cost |
|---|---|---|---|
| 1 | `crewai` | CrewAI importable **and** LLM key present | Token cost only |
| 2 | `llm` | no crewai, but an OpenAI-compatible key/base URL | Token cost only |
| 3 | `fallback` | nothing configured (default) | Free, offline, deterministic |

The facade returns one `HandleResult` (`draft`, `classification`, `priority`, `summary`,
`sources`, `escalate`, `confidence`, `engine`) no matter which engine ran — **flows and the
UI are engine-agnostic**.

## Decision 2 — The hierarchical crew (CrewAI, `.venv312`)

CrewAI requires Python ≤ 3.13, so it lives in a **second venv** (`.venv312`) created by
`scripts/setup-ai.sh`. `crew_support.py` builds:

- **Support Manager** (manager agent) — orchestrates, delegates, decides human handoff
- **Ticket Router** — classifies + prioritizes every ticket
- **Knowledge Agent** — grounds answers in tenant knowledge
- **Support Agent** — drafts professional replies
- **Escalation Agent** — decides when a human must take over

Process config keeps every crew run bounded (`max_iter=2`, `max_rpm=5`) so a single ticket
is cheap. If crewai isn't available the same semantics run through `direct_engine` or
`fallback_engine`, so behavior is identical, cost is zero.

## Decision 3 — Per-tenant RAG, isolated by construction

- `app/services/embeddings.py` — provider `hash` (offline, dim 384, default) · `openai` · `local`
- `app/services/vector.py` — `numpy` store (JSON file per namespace, default) or `qdrant`
- **Namespaces are `<org_id>` scoped.** Every search is a vector-store query on that
  namespace only; cross-tenant retrieval is impossible even if a route is misused.
- `app/services/knowledge_service.py` — parse (pypdf / python-docx / trafilatura / markdown),
  chunk, embed, index; deletes remove vectors atomically. Upload, URL ingestion, and FAQ
  sources all land in the same namespace.

## Decision 4 — Checkpointed, resumable flows

`app/flows/` implement a tiny durable workflow runner over `FlowRun`:

```
ticket:     start → classify → [escalate → awaiting_approval] → publish → completed
escalation: start → send → completed
feedback:   start → collect → completed
```

- State lives in `FlowRun.checkpoint` (JSON). Approval/rejection resumes from the checkpoint —
  nothing is recomputed or lost.
- `awaiting_approval` runs show in the Flows UI with **Approve & publish** / **Reject draft**.
- Every publish is audited (`flow.ticket.approved_and_published`, …) and tagged with the
  engine + knowledge sources used (traceability).

## API surface (added)

```
GET/POST      /workspaces/{slug}/knowledge            list / upload (multipart)
POST          /workspaces/{slug}/knowledge/search     semantic search (top-k, scores)
DELETE        /workspaces/{slug}/knowledge/{id}       delete + drop vectors
POST          /workspaces/{slug}/knowledge/ingest-url  fetch public URL
POST          /workspaces/{slug}/knowledge/faq         add Q&A doc
GET           /workspaces/{slug}/knowledge/tags        tag counts
GET/POST      /workspaces/{slug}/tickets              list / create
GET           /workspaces/{slug}/tickets/{id}         detail (messages)
POST          /workspaces/{slug}/tickets/{id}/handle  run the AI crew → draft + flow
POST          /workspaces/{slug}/tickets/{id}/resume   approve / reject the checkpoint
GET           /workspaces/{slug}/flows                recent runs
POST          /workspaces/{slug}/flows/trigger        escalation / feedback flows
POST          /workspaces/{slug}/flows/{id}/resume    resume a checkpoint
GET/PATCH     /workspaces/{slug}/agents               list / configure crew agents
GET           /workspaces/{slug}/agents/engine        active engine + capability status
```

## Frontend (added in this volume)

- **Knowledge** — drag & drop upload with progress, URL + FAQ ingestion, semantic search
  with relevance scores, tags, delete.
- **Tickets** — list with status/priority filters, conversation thread, **Handle with AI**,
  approval card (draft + sources + approve/reject).
- **Flows** — run timeline, expandable input/checkpoint/output JSON, resume actions.
- **Agents** — engine status card (CrewAI / provider / vector store) + per-agent enable/edit.
- New primitives: `textarea`, `status-badge`.

## Tests (target: 34 passing on `.venv312`)

`test_knowledge.py` · `test_tickets.py` · `test_flows_agents.py` · `test_crew.py`

Coverage: upload+search, tag counts, **tenant KB isolation**, delete-removes-vectors,
422 on unsupported files, ticket CRUD, AI handle with sources, urgent→approval→publish,
draft rejection, escalation/feedback runs, per-tenant run isolation, agent seeding,
engine status, and a CrewAI construction smoke test (Python 3.12 only).

## Definition of Done (Volume 2)

- [ ] Backend suite green on `.venv` (3.14, crew test skipped) **and** `.venv312` (3.12, all 34)
- [ ] Frontend `typecheck` + production `build` green
- [ ] Zero-key demo: register → create workspace → upload FAQ → search it → handle a ticket
- [ ] Urgent ticket pauses at `awaiting_approval` → approve → message appears + ticket resolved
- [ ] Knowledge from tenant A never answers tenant B (isolation test green)
