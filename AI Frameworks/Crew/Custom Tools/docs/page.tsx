import {
  Code2,
  Hammer,
  Layers,
  Lock,
  Rocket,
  TerminalSquare,
} from "lucide-react";
import Link from "next/link";

import { Navbar } from "@/components/landing/navbar";
import { Footer } from "@/components/landing/footer";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

function Code({ children }: { children: string }) {
  return (
    <pre className="overflow-x-auto rounded-lg border border-border bg-muted/50 p-4 text-xs leading-relaxed text-foreground">
      <code>{children}</code>
    </pre>
  );
}

function Section({
  icon: Icon,
  id,
  title,
  desc,
  children,
}: {
  icon: React.ComponentType<{ className?: string }>;
  id: string;
  title: string;
  desc: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24">
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
          <Icon className="h-4.5 w-4.5 text-primary" />
        </div>
        <div>
          <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
          <p className="text-sm text-muted-foreground">{desc}</p>
        </div>
      </div>
      <div className="mt-4 space-y-4">{children}</div>
    </section>
  );
}

const SECTIONS = [
  { href: "#overview", label: "Overview" },
  { href: "#architecture", label: "Architecture" },
  { href: "#quickstart", label: "Quick start" },
  { href: "#auth", label: "Auth & API" },
  { href: "#widget", label: "Public widget" },
  { href: "#jobs", label: "Jobs & billing" },
  { href: "#deploy", label: "Deployment" },
];

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="mx-auto flex max-w-6xl gap-10 px-4 py-12 sm:px-6">
        <aside className="hidden w-52 shrink-0 lg:block">
          <div className="sticky top-24 space-y-1">
            {SECTIONS.map((section) => (
              <a
                key={section.href}
                href={section.href}
                className="block rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                {section.label}
              </a>
            ))}
            <div className="pt-3">
              <Link href="/register" className="block rounded-md bg-primary/10 px-3 py-2 text-sm font-medium text-primary hover:bg-primary/15">
                Start free →
              </Link>
            </div>
          </div>
        </aside>

        <div className="min-w-0 max-w-3xl flex-1 space-y-12">
          <div>
            <Badge variant="secondary">Developer docs</Badge>
            <h1 className="mt-3 text-4xl font-bold tracking-tight">TenantDesk AI documentation</h1>
            <p className="mt-3 text-muted-foreground">
              A multi-tenant AI support platform: FastAPI backend, Next.js frontend, CrewAI
              orchestrator, per-tenant RAG and quota enforcement. Deployable entirely on a free
              stack.
            </p>
          </div>

          <Section icon={Layers} id="overview" title="Overview" desc="What ships in this repository">
            <Card>
              <CardHeader>
                <CardTitle>Monorepo layout</CardTitle>
                <CardDescription>Separate deployable units, one stack</CardDescription>
              </CardHeader>
              <CardContent>
                <Code>{`apps/
  backend/     FastAPI + SQLAlchemy + Alembic API (port 8000)
  frontend/    Next.js 15 app router UI (port 3000)
  admin/       CLI helpers for super-admins
docker/        Dockerfiles + docker-compose.yml
docs/          Deep-dive engineering docs
scripts/       Dev tooling (setup, dev, test, deploy)
tests/         End-to-end integration suite`}</Code>
              </CardContent>
            </Card>
          </Section>

          <Section
            icon={Rocket}
            id="architecture"
            title="Architecture"
            desc="How the pieces fit together"
          >
            <Card>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Each tenant is an <code className="rounded bg-muted px-1">Organization</code>.
                  Every request resolves the caller&apos;s membership and scopes all queries to
                  <code className="rounded bg-muted px-1">organization_id</code> — tenant isolation
                  is enforced in the service layer, never in the client.
                </p>
                <p className="text-sm text-muted-foreground">
                  The AI engine auto-detects <b>CrewAI</b> (full orchestration) and falls back to a
                  deterministic offline rule engine when no API keys are set, so the whole stack
                  runs for free. Embeddings default to a local hash index; Qdrant is supported.
                </p>
                <p className="text-sm text-muted-foreground">
                  Long-running work (indexing, crawling, reports) runs as persisted jobs with
                  progress + checkpoints; the runner is swappable for Redis/Celery without changing
                  the API contract.
                </p>
              </CardContent>
            </Card>
          </Section>

          <Section
            icon={TerminalSquare}
            id="quickstart"
            title="Quick start"
            desc="Run the full stack in minutes"
          >
            <Card>
              <CardContent className="space-y-3">
                <Code>{`# Backend
cd apps/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # defaults run everything offline
python -m scripts.create_superadmin  # optional
uvicorn app.main:app --reload

# Frontend (new terminal)
cd apps/frontend
npm install
npm run dev                    # http://localhost:3000`}</Code>
                <p className="text-sm text-muted-foreground">
                  Sign up, create a workspace, upload a document, then open the Tickets page and
                  click <b>Handle with AI</b>. No API keys required.
                </p>
              </CardContent>
            </Card>
          </Section>

          <Section
            icon={Lock}
            id="auth"
            title="Auth & API"
            desc="Token-based, role-scoped, audited"
          >
            <Card>
              <CardContent className="space-y-3">
                <Code>{`POST /api/v1/auth/register   {"email":"you@co.com","password":"..."}
POST /api/v1/auth/login      -> { access_token, user, memberships }
GET  /api/v1/workspaces      -> list your tenants
Authorization: Bearer <token>`}</Code>
                <p className="text-sm text-muted-foreground">
                  Roles: <b>owner</b> (billing, members, widget), <b>admin</b>, <b>agent</b>.
                  Sensitive actions are written to the per-workspace audit trail.
                </p>
                <Code>{`GET  /api/v1/workspaces/{slug}/analytics/overview
GET  /api/v1/workspaces/{slug}/billing/summary
GET  /api/v1/workspaces/{slug}/jobs
POST /api/v1/workspaces/{slug}/flows/{run_id}/resume   {"approved": true}`}</Code>
              </CardContent>
            </Card>
          </Section>

          <Section
            icon={Code2}
            id="widget"
            title="Public widget"
            desc="Embed AI chat on any website"
          >
            <Card>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Owners enable the widget from workspace settings, which generates a per-tenant
                  token. Public endpoints need no user login — only the widget token.
                </p>
                <Code>{`# Enable the widget (owner only, inside the app settings)
POST /api/v1/workspaces/{slug}/widget/enable
GET  /api/v1/workspaces/{slug}/widget/config    # -> widget_token, widget_url

# Public embed (no auth — just the token)
POST /api/v1/public/{slug}/chat
  headers: { "X-Widget-Token": "..." }
  body:    { "message": "how do I reset my password" }`}</Code>
                <p className="text-sm text-muted-foreground">
                  Widget calls consume the same monthly AI-request quota as the internal app and
                  can hand off to a human ticket via{" "}
                  <code className="rounded bg-muted px-1">/api/v1/public/{`{slug}`}/tickets</code>.
                </p>
              </CardContent>
            </Card>
          </Section>

          <Section
            icon={Hammer}
            id="jobs"
            title="Jobs & billing"
            desc="Async work and plan enforcement"
          >
            <Card>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">
                  Four job types ship ready to use: <b>index_document</b>, <b>crawl_website</b>,{" "}
                  <b>batch_faq</b> and <b>weekly_report</b>. Failed jobs keep their checkpoint and
                  can be retried.
                </p>
                <Code>{`POST /api/v1/workspaces/{slug}/jobs
  { "job_type": "crawl_website", "url": "https://example.com/docs", "max_pages": 10 }
POST /api/v1/workspaces/{slug}/jobs/{job_id}/retry`}</Code>
                <p className="text-sm text-muted-foreground">
                  Plans (free / pro / enterprise) define monthly limits for AI requests, knowledge
                  documents, storage and seats. Limits are enforced on the backend and reset on
                  the workspace billing date.
                </p>
              </CardContent>
            </Card>
          </Section>

          <Section
            icon={Rocket}
            id="deploy"
            title="Deployment"
            desc="Docker Compose + free-tier guides"
          >
            <Card>
              <CardContent className="space-y-3">
                <Code>{`cd repo-root
docker compose up --build          # api + web
docker compose --profile worker up # + async job worker (db-backed queue)`}</Code>
                <p className="text-sm text-muted-foreground">
                  Swap the SQLite default for PostgreSQL, set{" "}
                  <code className="rounded bg-muted px-1">AI_ENGINE</code> to{" "}
                  <code className="rounded bg-muted px-1">crewai</code> (add your LLM keys) for
                  full orchestration, and point a reverse proxy at the frontend. Deployment notes
                  for Render/Fly.io/Railway are in the repository docs.
                </p>
              </CardContent>
            </Card>
          </Section>

          <div className="rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-700 p-8 text-center text-white">
            <h2 className="text-2xl font-bold tracking-tight">Try it for free</h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-white/80">
              Create a workspace, upload a document and let the AI crew answer tickets — no credit
              card needed.
            </p>
            <Link href="/register">
              <span className="mt-6 inline-block rounded-lg bg-white px-5 py-2.5 text-sm font-semibold text-indigo-700 hover:bg-white/90">
                Get started →
              </span>
            </Link>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
