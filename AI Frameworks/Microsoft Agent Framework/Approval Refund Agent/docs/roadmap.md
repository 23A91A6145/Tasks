# 🗺️ Learning Roadmap & Future Enhancements

## Learning Roadmap (how this project maps to the 5 volumes)

| Volume | Focus | Delivered here |
|---|---|---|
| **1. Foundation** | Why HITL, enterprise AI safety, environment setup | `README.md`, `docs/architecture.md`, `.env.example` |
| **2. Approval Workflow** | Agent, sensitive tool, DevUI approval, testing | `app/agent.py`, `app/refund_tool.py`, `templates/dashboard.html`, `run_demo.py` |
| **3. Professional Features** | Dashboard, customer profiler, approval form, stats, notifications | `app/services.py`, dashboard sections, notification outbox |
| **4. Production & Security** | Audit logs, config, RBAC, rate limiting, error handling, testing | `app/settings.py`, `docs/security.md`, `docs/testing.md` |
| **5. Deployment & Portfolio** | Docker, GitHub, portfolio | `Dockerfile`, `docker-compose.yml`, `docs/deployment.md`, `docs/PORTFOLIO.md` |

## Core Concepts Exercised

`Human-in-the-Loop` · `Tool Approval` · `Workflow Pause & Resume` · `Checkpointing` ·
`RBAC` · `Audit Logging` · `SLA leases` · `Anti-fraud duplicate blocks` ·
`AI Governance` · `Responsible AI` · `Notification templating`

## Phase 5.3 — Future Enhancements

Priority-ordered backlog:

1. **PostgreSQL + Redis** — replace JSON persistence and in-memory rate limits.
2. **Foundry Memory** — long-term agent memory via `agent_framework` memory providers.
3. **MCP Tools** — expose the refund tool over Model Context Protocol (`SupportsMCPTool`).
4. **A2A** — agent-to-agent protocol for multi-agent review chains.
5. **Multi-Agent Review** — a second "auditor" agent that double-checks approvals.
6. **Real email/Slack/Teams notifications** — wire the outbox to SMTP and webhooks.
7. **Analytics dashboard** — charts for approval velocity, fraud flags, reviewer performance.
8. **Real LLM gate** — replace the heuristic parser with a fully agentic flow once an LLM
   provider (Groq/Ollama) is configured, keeping the same approval gate.

## Portfolio Next Steps

- Record a **demo GIF** of the DevUI (approve + reject flows) into `docs/screenshots/`.
- Add **architecture + workflow PNGs** exported from the Mermaid diagrams.
- Publish the repo (see `docs/deployment.md` §4) and link it on LinkedIn/GitHub.
