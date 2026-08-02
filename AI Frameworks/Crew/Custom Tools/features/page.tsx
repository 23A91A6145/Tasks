import {
  ArrowRight,
  BarChart3,
  Bot,
  BookOpen,
  CreditCard,
  Hammer,
  ShieldCheck,
  Ticket,
  Users,
  Workflow,
} from "lucide-react";
import Link from "next/link";

import { Navbar } from "@/components/landing/navbar";
import { Footer } from "@/components/landing/footer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const MODULES: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  tag: string;
  points: string[];
}[] = [
  {
    icon: ShieldCheck,
    title: "Multi-tenant isolation",
    tag: "Core",
    points: [
      "Row-level tenant scoping on every query — knowledge, tickets and users never leak",
      "Membership + role model (owner → agent) enforced via middleware on all endpoints",
      "Audit trail of every sensitive action per workspace",
    ],
  },
  {
    icon: BookOpen,
    title: "Knowledge base",
    tag: "Vol 2",
    points: [
      "Upload PDF, DOCX, Markdown and TXT — or paste FAQs directly",
      "Ingest any URL via a built-in website crawler",
      "Free offline embedding + cosine vector search (Qdrant optional)",
      "Per-tenant storage with file-type and size validation",
    ],
  },
  {
    icon: Bot,
    title: "Hierarchical AI crew",
    tag: "Vol 2",
    points: [
      "Manager agent routes work to support, escalation and report agents",
      "CrewAI orchestrator with an offline rule-engine fallback",
      "Per-tenant agent configuration and toggles",
    ],
  },
  {
    icon: Ticket,
    title: "Ticket triage",
    tag: "Vol 2",
    points: [
      "Automatic classification, priority detection and AI summaries",
      "Retrieval-grounded replies citing your knowledge sources",
      "Resolution flow with a human approval checkpoint",
    ],
  },
  {
    icon: Workflow,
    title: "Checkpointed flows",
    tag: "Vol 2",
    points: [
      "Pause, resume and retry long-running workflows",
      "Human-in-the-loop approval for escalations",
      "Feedback flows that learn from outcomes",
    ],
  },
  {
    icon: Hammer,
    title: "Long-running jobs",
    tag: "Vol 4",
    points: [
      "Document re-indexing, website crawling, FAQ batches and weekly reports",
      "Progress tracking, checkpoints and one-click retry",
      "Swap-in ready for Redis/Celery without changing the API contract",
    ],
  },
  {
    icon: BarChart3,
    title: "Usage analytics",
    tag: "Vol 4",
    points: [
      "Requests, tokens and estimated cost per month",
      "Ticket, priority and resolution-time metrics",
      "Knowledge growth, workflow performance and engine distribution",
    ],
  },
  {
    icon: CreditCard,
    title: "Plans & quotas",
    tag: "Vol 4",
    points: [
      "Free / Pro / Enterprise catalog enforced server-side",
      "Monthly request, document, storage and seat limits",
      "Usage meters on the billing page with one-click plan switching",
    ],
  },
  {
    icon: Users,
    title: "Team management",
    tag: "Core",
    points: [
      "Invite members with role-based permissions",
      "Seat quotas per plan",
      "Workspace switching from anywhere in the app",
    ],
  },
];

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <section className="mx-auto max-w-6xl px-4 pb-16 pt-14 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <Badge variant="secondary">Feature tour</Badge>
          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Everything a modern AI support platform needs
          </h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Nine modules across four volumes — each one isolated per tenant and built on a free,
            open-source stack.
          </p>
        </div>

        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {MODULES.map((module) => (
            <Card key={module.title} className="flex flex-col transition-shadow hover:shadow-md">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <module.icon className="h-5 w-5 text-primary" />
                  </div>
                  <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                    {module.tag}
                  </span>
                </div>
                <CardTitle className="mt-3">{module.title}</CardTitle>
              </CardHeader>
              <CardContent className="flex-1">
                <ul className="space-y-2.5">
                  {module.points.map((point) => (
                    <li key={point} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                      {point}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="mt-12 text-center">
          <Link href="/register">
            <Button size="lg">
              Start free
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
}
