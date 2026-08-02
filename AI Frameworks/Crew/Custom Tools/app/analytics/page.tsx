"use client";

import { useCallback, useEffect, useState } from "react";
import {
  BarChart3,
  BookOpen,
  Bot,
  Clock,
  DollarSign,
  Gauge,
  Percent,
  Ticket,
  TrendingUp,
  Zap,
} from "lucide-react";

import {
  apiFetch,
  type AnalyticsOverview,
  type DailyCount,
} from "@/lib/api";
import { useSession } from "@/lib/session";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { KpiCard, KpiSkeleton } from "@/components/dashboard/kpi-card";
import { UsageChart } from "@/components/dashboard/usage-chart";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";

function MiniBars({
  data,
  accent = "bg-primary/70",
}: {
  data: { label: string; value: number; hint?: string }[];
  accent?: string;
}) {
  const max = Math.max(1, ...data.map((d) => d.value));
  return (
    <div className="space-y-3">
      {data.map((item) => (
        <div key={item.label}>
          <div className="mb-1 flex items-center justify-between text-xs">
            <span className="capitalize text-muted-foreground">{item.label}</span>
            <span className="font-medium">
              {item.value}
              {item.hint && <span className="ml-1 text-muted-foreground">({item.hint})</span>}
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-muted">
            <div
              className={`h-full rounded-full ${accent}`}
              style={{ width: `${item.value === 0 ? 2 : Math.max(6, (item.value / max) * 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function FlowTable({ data }: { data: AnalyticsOverview }) {
  const flows = data.agents.flows;
  if (flows.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-muted-foreground">
        No workflow runs in the last 30 days yet.
      </p>
    );
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs uppercase tracking-wider text-muted-foreground">
            <th className="pb-2 pr-4 font-medium">Flow</th>
            <th className="pb-2 pr-4 font-medium">Runs</th>
            <th className="pb-2 pr-4 font-medium">Completed</th>
            <th className="pb-2 pr-4 font-medium">Awaiting review</th>
            <th className="pb-2 pr-4 font-medium">Rejected</th>
            <th className="pb-2 font-medium">Failed</th>
          </tr>
        </thead>
        <tbody>
          {flows.map((flow) => (
            <tr key={flow.flow} className="border-b border-border/60 last:border-0">
              <td className="py-2.5 pr-4 font-medium capitalize">{flow.flow}</td>
              <td className="py-2.5 pr-4">{flow.total}</td>
              <td className="py-2.5 pr-4 text-success">{flow.completed}</td>
              <td className="py-2.5 pr-4 text-warning">{flow.awaiting_approval}</td>
              <td className="py-2.5 pr-4">{flow.rejected}</td>
              <td className="py-2.5 text-destructive">{flow.failed}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function AnalyticsPage() {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [data, setData] = useState<AnalyticsOverview | null>(null);

  const slug = activeWorkspace?.slug;

  const load = useCallback(async () => {
    if (!slug) return;
    const result = await apiFetch<AnalyticsOverview>(
      `/api/v1/workspaces/${slug}/analytics/overview`,
    );
    setData(result);
  }, [slug]);

  useEffect(() => {
    if (!slug) return;
    load().catch(() => toast({ title: "Could not load analytics", variant: "error" }));
  }, [slug, load, toast]);

  if (!data) {
    return (
      <div className="space-y-5">
        <Skeleton className="h-8 w-56" />
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <KpiSkeleton />
          <KpiSkeleton />
          <KpiSkeleton />
          <KpiSkeleton />
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <Skeleton className="h-72" />
          <Skeleton className="h-72" />
        </div>
      </div>
    );
  }

  const { summary, usage, tickets, knowledge, agents } = data;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
            <BarChart3 className="h-5 w-5 text-primary" /> Analytics
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Usage, performance and cost for your workspace over the last 30 days.
          </p>
        </div>
        <Badge variant="secondary" className="capitalize">
          {summary.plan} plan
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard
          title="AI requests / month"
          value={summary.requests_month.toLocaleString()}
          hint={summary.request_limit === 0 ? "unlimited" : `limit ${summary.request_limit.toLocaleString()}`}
          icon={Zap}
        />
        <KpiCard
          title="Request limit used"
          value={`${summary.request_percent}%`}
          hint="of the current plan's monthly budget"
          icon={Gauge}
          accent="warning"
        />
        <KpiCard
          title="Tokens this month"
          value={summary.tokens_month.toLocaleString()}
          hint="input + output across LLM calls"
          icon={TrendingUp}
        />
        <KpiCard
          title="Est. cost / month"
          value={`$${summary.est_cost_month.toFixed(2)}`}
          hint="gpt-4o-mini class pricing"
          icon={DollarSign}
          accent="warning"
        />
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard
          title="Open tickets"
          value={summary.tickets_open}
          hint="new, open or pending"
          icon={Ticket}
        />
        <KpiCard
          title="Resolution rate (7d)"
          value={`${summary.resolution_rate_7d}%`}
          hint={`${summary.tickets_resolved_7d} resolved in 7 days`}
          icon={Percent}
          accent="success"
        />
        <KpiCard
          title="Knowledge docs"
          value={summary.knowledge_docs}
          hint={`${summary.knowledge_chunks} chunks indexed`}
          icon={BookOpen}
        />
        <KpiCard
          title="Active agents"
          value={summary.active_agents}
          hint="enabled agent roles"
          icon={Bot}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>AI requests — last 30 days</CardTitle>
            <CardDescription>
              {usage.total_requests.toLocaleString()} total · {usage.total_tokens.toLocaleString()}{" "}
              tokens
            </CardDescription>
          </CardHeader>
          <CardContent>
            <UsageChart data={usage.daily_requests} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Breakdown by type</CardTitle>
            <CardDescription>Where your AI budget is going</CardDescription>
          </CardHeader>
          <CardContent>
            {usage.by_kind.length === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">
                No usage recorded yet — run a ticket or search your knowledge base.
              </p>
            ) : (
              <MiniBars
                data={usage.by_kind.map((k) => ({
                  label: k.kind,
                  value: k.calls,
                  hint: `${k.tokens.toLocaleString()} tokens`,
                }))}
              />
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Tickets by status</CardTitle>
            <CardDescription>{tickets.total} created in 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <MiniBars
              data={tickets.by_status.map((s) => ({ label: s.status, value: s.count }))}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Priority mix</CardTitle>
            <CardDescription>Distribution of incoming volume</CardDescription>
          </CardHeader>
          <CardContent>
            <MiniBars
              data={tickets.by_priority.map((p) => ({ label: p.priority, value: p.count }))}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resolution time</CardTitle>
            <CardDescription>Time from creation to resolution</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center justify-center gap-2 py-8">
            <Clock className="h-8 w-8 text-primary" />
            <p className="text-3xl font-semibold tracking-tight">
              {tickets.avg_resolution_hours}h
            </p>
            <p className="text-sm text-muted-foreground">average resolution time</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Knowledge growth</CardTitle>
            <CardDescription>Documents added per day</CardDescription>
          </CardHeader>
          <CardContent>
            <UsageChart data={knowledge.daily_added} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Knowledge sources</CardTitle>
            <CardDescription>How your knowledge base was built</CardDescription>
          </CardHeader>
          <CardContent>
            <MiniBars
              data={knowledge.by_source.map((s) => ({ label: s.source, value: s.count }))}
            />
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Workflow performance</CardTitle>
            <CardDescription>{agents.total_runs} runs in the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <FlowTable data={data} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Engine distribution</CardTitle>
            <CardDescription>AI engine used per run</CardDescription>
          </CardHeader>
          <CardContent>
            {agents.engine_distribution.length === 0 ? (
              <p className="py-6 text-center text-sm text-muted-foreground">No runs yet.</p>
            ) : (
              <MiniBars
                data={agents.engine_distribution.map((e) => ({ label: e.engine, value: e.count }))}
              />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
