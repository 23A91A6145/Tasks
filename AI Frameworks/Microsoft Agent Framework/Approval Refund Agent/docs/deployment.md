# 🚀 Deployment Guide

## 1. Local (Developer)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # optional; defaults are safe
python main.py                # → http://127.0.0.1:8000
```

Run the offline demo runner and the test suite:

```bash
python run_demo.py
python -m pytest -q
```

## 2. Docker

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f
```

- `logs/` and `checkpoints/` are volume-mounted so audit trails and workflow state
  survive container restarts.
- A `HEALTHCHECK` calls `/api/health` every 30s.
- Environment is injected via `env_file: .env` plus compose overrides.

## 3. Cloud (Free Tier)

The service is a standard FastAPI app behind uvicorn, so it runs on any container host.

- **Render** (free): connect the GitHub repo → *Docker* runtime → start command `python main.py`.
- **Fly.io** (free tier): `fly launch` with `fly.toml` exposing `:8000`.
- **Railway**: `railway up` with a container service.

Production notes:
- Set `LLM_PROVIDER=groq` + `GROQ_API_KEY` (free tier) or `LLM_PROVIDER=ollama` for local inference.
- Swap `MAX_AUTO_APPROVE_AMOUNT=0` to force **every** refund through the human gate.
- Persist `checkpoints/` on an attached volume; upgrade to PostgreSQL later (Phase 5.3).

## 4. GitHub Repository

```bash
git init
git add .
git commit -m "Approval-Gated Refund Agent (HITL) - Microsoft Agent Framework"
git branch -M main
git remote add origin https://github.com/<username>/approval-gated-refund-agent.git
git push -u origin main
```

Add to the repo: `README.md`, `docs/`, `docs/diagrams/`, `docs/screenshots/`, `.env.example`,
a demo GIF, and the test report in `docs/testing.md`.
