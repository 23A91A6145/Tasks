"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Activity as ActivityIcon,
  Building2,
  Bot,
  BookOpen,
  Ticket,
  Workflow,
  CreditCard,
  BarChart3,
  Users,
  UserRound,
  Plus,
  ShieldCheck,
  Rocket,
  Zap,
} from "lucide-react";
import Link from "next/link";

import { apiFetch, type Activity, type WorkspaceStats } from "@/lib/api";
import { useSession } from "@/lib/session";
import { formatDate } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";
import { KpiCard, KpiSkeleton } from "@/components/dashboard/kpi-card";
import { UsageChart } from "@/components/dashboard/usage-chart";
import { ActivityList, ActivityListSkeleton } from "@/components/dashboard/activity-list";

const MODULES = [
  { href: "/app/knowledge", label: "Knowledge", description: "Isolated RAG knowledge base", icon: BookOpen, tag: "Vol 2" },
  { href: "/app/agents", label: "Agents", description: "Hierarchical AI support crew", icon: Bot, tag: "Vol 2" },
  { href: "/app/tickets", label: "Tickets", description: "Ticket triage & resolution", icon: Ticket, tag: "Vol 2" },
  { href: "/app/flows", label: "Flows", description: "Checkpointed AI workflows", icon: Workflow, tag: "Vol 2" },
  { href: "/app/analytics", label: "Analytics", description: "Usage & performance insights", icon: BarChart3, tag: "Vol 4" },
  { href: "/app/billing", label: "Billing", description: "Plans & usage limits", icon: CreditCard, tag: "Vol 4" },
];

function EmptyWorkspace() {
  const { user, createWorkspace } = useSession();
  const { toast } = useToast();
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      await createWorkspace(name.trim());
      toast({ title: "Workspace created — welcome aboard!", variant: "success" });
    } catch (error) {
      toast({
        title: "Could not create workspace",
        description: error instanceof Error ? error.message : "Something went wrong",
        variant: "error",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-lg flex-col items-center gap-4 py-16 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg">
        <Rocket className="h-8 w-8" />
      </div>
      <h1 className="text-2xl font-semibold tracking-tight">Let&apos;s set up your workspace</h1>
      <p className="text-muted-foreground">
        Hi {user?.full_name.split(" ")[0]}, you&apos;re one step away from your AI support crew.
        A workspace gives you an isolated knowledge base, agents and team.
      </p>
      <Card className="mt-2 w-full p-5">
        <Label htmlFor="ws-setup">Workspace name</Label>
        <div className="mt-1.5 flex gap-2">
          <Input
            id="ws-setup"
            placeholder="e.g. Acme Support"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit()}
          />
          <Button onClick={submit} disabled={loading || !name.trim()}>
            {loading ? <Spinner /> : <Plus className="h-4 w-4" />}
            Create
          </Button>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          You can change or add more workspaces anytime.
        </p>
      </Card>
    </div>
  );
}

function DashboardContent() {
  const { user, activeWorkspace } = useSession();
  const [stats, setStats] = useState<WorkspaceStats | null>(null);
  const [activity, setActivity] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeWorkspace) return;
    setLoading(true);
    Promise.all([
      apiFetch<WorkspaceStats>(`/api/v1/workspaces/${activeWorkspace.slug}/stats`),
      apiFetch<Activity[]>(`/api/v1/workspaces/${activeWorkspace.slug}/activity`),
    ])
      .then(([statsData, activityData]) => {
        setStats(statsData);
        setActivity(activityData);
      })
      .finally(() => setLoading(false));
  }, [activeWorkspace]);

  if (loading || !stats) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-72" />
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <KpiSkeleton />
          <KpiSkeleton />
          <KpiSkeleton />
          <KpiSkeleton />
        </div>
        <div className="grid gap-4 lg:grid-cols-5">
          <Skeleton className="h-72 lg:col-span-3" />
          <Skeleton className="h-72 lg:col-span-2" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Welcome back, {user?.full_name.split(" ")[0]}
          </h1>
          <p className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
            <Building2 className="h-4 w-4" />
            {activeWorkspace?.name}
            <Badge variant={stats.plan === "free" ? "secondary" : "success"}>
              {stats.plan} plan
            </Badge>
          </p>
        </div>
        <Button size="sm">
          <Link href="/app/knowledge" className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add knowledge
          </Link>
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard
          title="Members"
          value={stats.member_count}
          hint="people in your workspace"
          icon={Users}
        />
        <KpiCard
          title="Your role"
          value={stats.your_role}
          hint="minimum permission level"
          icon={ShieldCheck}
          accent="success"
        />
        <KpiCard
          title="Events (7d)"
          value={stats.activity_7d.reduce((sum, d) => sum + d.count, 0)}
          hint="workspace activity"
          icon={ActivityIcon}
          accent="warning"
        />
        <KpiCard
          title="Plan"
          value={stats.plan}
          hint={`created ${formatDate(activeWorkspace?.created_at ?? "")}`}
          icon={Zap}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Activity — last 7 days</CardTitle>
            <CardDescription>Total events: {stats.total_activity}</CardDescription>
          </CardHeader>
          <CardContent>
            <UsageChart data={stats.activity_7d} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent activity</CardTitle>
            <CardDescription>Audit trail for this workspace</CardDescription>
          </CardHeader>
          <CardContent className="max-h-72 overflow-y-auto">
            <ActivityList items={activity} />
          </CardContent>
        </Card>
      </div>

      <div>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Your AI platform
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {MODULES.map((module) => (
            <Link key={module.href} href={module.href} className="group">
              <Card className="h-full transition-all group-hover:border-primary/40 group-hover:shadow-md">
                <CardContent className="flex items-start gap-4 p-5">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <module.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <p className="font-medium">{module.label}</p>
                      <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
                        {module.tag}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-muted-foreground">{module.description}</p>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Next steps</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2 text-sm text-muted-foreground sm:flex-row sm:items-center sm:gap-8">
          <p className="flex items-center gap-2">
            <UserRound className="h-4 w-4 text-primary" />
            Invite teammates from the <Link href="/app/users" className="font-medium text-primary hover:underline">Users</Link> page
          </p>
          <p className="flex items-center gap-2">
            <Bot className="h-4 w-4 text-primary" />
            <Link href="/app/knowledge" className="font-medium text-primary hover:underline">Add documents</Link>{" "}
            to ground your AI crew
          </p>
          <p className="flex items-center gap-2">
            <CreditCard className="h-4 w-4 text-primary" />
            Track usage &amp; plans on the <Link href="/app/billing" className="font-medium text-primary hover:underline">Billing</Link> page
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

export default function DashboardPage() {
  const { workspaces, loading } = useSession();

  if (loading) return <FullScreenLoaderStub />;

  return workspaces.length === 0 ? <EmptyWorkspace /> : <DashboardContent />;
}

function FullScreenLoaderStub() {
  return (
    <div className="flex h-64 items-center justify-center">
      <Spinner className="h-8 w-8 text-primary" />
    </div>
  );
}
