# TenantDesk AI — Full Project Plan

> **Product:** Multi-Tenant AI Support Platform (SaaS)
> **Tagline:** Every company gets its own AI support crew, its own knowledge, its own space.
> **Stack:** Next.js · FastAPI · CrewAI · PostgreSQL · Qdrant · Docker · Free-tier deployment

---

## 1. What we are building

A production-grade, multi-tenant SaaS platform where an organization (a **tenant**) signs up,
creates a **workspace**, and gets:

- their own AI support crew (hierarchical CrewAI agents),
- their own **isolated knowledge base** (RAG over their documents),
- their own **tickets / flows / users / analytics / usage limits**,
- **complete data isolation** between tenants.

Comparable products: Zendesk AI, Intercom AI, Freshdesk AI, GitHub Copilot for docs.

## 2. Why

- **Skill showcase:** end-to-end AI SaaS (auth, tenancy, agents, RAG, MCP, SaaS metering, deploy).
- **Real market fit:** every company wants a branded AI support assistant without building infra.
- **All free/open tools:** 0-cost to build and learn, deploy on free tiers.

## 3. The 5 Volumes (roadmap)

### Volume 1 — SaaS Foundations & Platform Core (THIS VOLUME)
**Goal:** a runnable multi-tenant platform: auth, workspaces, roles, tenant isolation, audit log, dashboard.

| Phase | Deliverable |
|---|---|
| 1.1 | Product planning docs (requirements, architecture, DB model, feature matrix) |
| 1.2 | Project setup (monorepo, Docker, env, scripts, CI-ready) |
| 1.3 | Authentication, multi-tenancy, RBAC, workspace CRUD, members, activity log |
| 1.4 | Professional UI/UX: landing, auth screens, dashboard shell, first pages |

### Volume 2 — AI Engine & Multi-Agent Platform
| Phase | Deliverable |
|---|---|
| 2.1 | CrewAI hierarchical crew (Manager → Router → Knowledge/Support/Escalation/Report agents) |
| 2.2 | CrewAI Flows: ticket flow, escalation flow, feedback flow; checkpoints, human-in-the-loop |
| 2.3 | Tenant knowledge system: upload PDF/DOCX/MD/FAQs, per-tenant namespaces |

### Volume 3 — Data, Tools & Intelligence
| Phase | Deliverable |
|---|---|
| 3.1 | RAG pipeline (chunk → embed → Qdrant → retrieve → LLM → answer) |
| 3.2 | MCP integration (filesystem, GitHub, browser, custom MCP servers) |
| 3.3 | Tool ecosystem (web search, calculator, email, calendar, CRM, ticket system) |

### Volume 4 — Production SaaS Features
| Phase | Deliverable |
|---|---|
| 4.1 | Plans & usage limits (Free / Pro / Enterprise; quotas, tokens, storage) |
| 4.2 | Long-running jobs (document indexing, crawling, reports; queue, retry, checkpoints) |
| 4.3 | Monitoring & analytics dashboards (usage, latency, success rate, cost) |

### Volume 5 — Productization & Deployment
| Phase | Deliverable |
|---|---|
| 5.1 | Professional UI/UX (public site, dashboards, billing, docs, dark/light) |
| 5.2 | Deployment (Vercel + Render/Railway + Postgres + Qdrant Docker; free tiers) |
| 5.3 | Portfolio & docs (README, API docs, diagrams, demo video, sample data, test guide) |

## 4. What / Where / How / When / Why — cheat sheet

| Question | Answer |
|---|---|
| **What** | Multi-tenant AI support SaaS with isolated knowledge + orchestrated agents |
| **Where** | Monorepo: `apps/frontend`, `apps/backend`, `docs`, `scripts`, `docker` |
| **How** | Next.js UI → FastAPI REST API → Postgres; future: CrewAI + Qdrant |
| **When** | Volume 1 now → Volumes 2–5 later; each volume ends runnable & demoable |
| **Why** | Portfolio capstone proving full-stack + AI engineering skill |

## 5. Concepts used

Multi-tenancy (shared DB, row-level tenant scoping) · RBAC role hierarchy · JWT access+refresh
tokens · bcrypt hashing · audit logging · UUID PKs · REST + OpenAPI · SQLAlchemy 2.0 ·
pydantic v2 validation · Docker Compose · CI-ready layout · accessible SaaS design system.

## 6. Free stack (0$ development)

| Layer | Tool |
|---|---|
| Frontend | Next.js 15 + React 19 + Tailwind CSS v4 + lucide icons |
| Backend | FastAPI + SQLAlchemy 2.0 + pydantic v2 |
| Auth | PyJWT + bcrypt (refresh rotation) |
| DB (dev) | SQLite (file, zero setup) |
| DB (prod) | PostgreSQL via Docker |
| Container | Docker Compose |
| Deploy (later) | Vercel (FE) + Render/Railway free (BE) + Qdrant Docker |

## 7. Key principles

1. **Isolation first** — every tenant query is scoped by membership; never trust the client.
2. **Least privilege** — roles gate every endpoint.
3. **Zero secrets in git** — `.env` only, `.env.example` committed.
4. **Runnable at every phase** — after each phase you can run and demo it.
5. **Laptop-friendly** — SQLite default, Docker optional, all tools free.
