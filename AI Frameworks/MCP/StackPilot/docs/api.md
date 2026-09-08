# 📡 StackPilot REST & SSE API Specification

Base URL: `http://localhost:8000/api/v1`

---

## 1. Projects API
* `POST /projects`: Register a new migration project.
  * Body: `{"name": "E-Commerce Monolith", "repo_path": "/path/to/repo", "description": "Legacy Node+Postgres"}`
* `GET /projects`: List all registered projects.
* `GET /projects/{id}`: Retrieve project metadata and historical runs.

---

## 2. Migration Runs API
* `POST /runs`: Trigger an autonomous migration analysis run.
  * Body:
    ```json
    {
      "project_id": "proj_123",
      "user_goal": "Migrate monolithic Node.js + PostgreSQL to microservices",
      "constraints": {
        "budget_yearly": 500000,
        "max_downtime_minutes": 30,
        "primary_focus": "security"
      }
    }
    ```
  * Response: `{"run_id": "run_999", "thread_id": "th_abc", "status": "QUEUED"}`
* `GET /runs/{id}`: Retrieve full execution state and findings.
* `GET /runs/{id}/stream`: Real-time Server-Sent Events (SSE) emitting node transitions and tool outputs.
* `POST /runs/{id}/resume`: Resume an interrupted or paused run.
* `POST /runs/{id}/simulate`: Run "What-If" parameter simulation using checkpointed state.

---

## 3. Human-in-the-Loop (HITL) Approvals API
* `GET /approvals`: List pending approval requests.
* `POST /approvals/{id}/approve`: Approve high-risk task and resume LangGraph execution.
* `POST /approvals/{id}/reject`: Reject task with feedback and trigger replanning.
* `POST /approvals/{id}/modify`: Update task arguments before resuming execution.

---

## 4. Evaluations API
* `POST /evaluations/run`: Execute benchmark evaluation against golden dataset.
* `GET /evaluations`: List historical evaluation run metrics.
