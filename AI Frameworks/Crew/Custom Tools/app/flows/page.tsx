"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, Check, ChevronDown, GitBranch, RotateCcw, X } from "lucide-react";

import { apiFetch, type FlowRun } from "@/lib/api";
import { useSession } from "@/lib/session";
import { timeAgo } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/ui/status-badge";
import { useToast } from "@/components/ui/toast";

const FLOW_LABELS: Record<string, { label: string; desc: string }> = {
  ticket: { label: "Ticket triage", desc: "Classify, draft and resolve incoming tickets." },
  escalation: { label: "Escalation", desc: "Hand off to a human when confidence is low." },
  feedback: { label: "Feedback", desc: "Collect ratings and learn from outcomes." },
};

const STEP_LABELS: Record<string, string> = {
  start: "Start",
  classify: "Classify with AI",
  publish: "Publish reply",
  done: "Done",
  send: "Send to human",
  collect: "Collect feedback",
};

function JsonBlock({ data }: { data: Record<string, unknown> }) {
  return (
    <pre className="max-h-72 overflow-auto rounded-md bg-muted/50 p-3 text-[11px] leading-relaxed text-muted-foreground">
      {JSON.stringify(data, null, 2)}
    </pre>
  );
}

function RunCard({ run, onResume }: { run: FlowRun; onResume: (run: FlowRun, approved: boolean) => void }) {
  const [open, setOpen] = useState(false);
  const meta = FLOW_LABELS[run.flow_key] ?? { label: run.flow_key, desc: "" };
  const stepLabel = STEP_LABELS[run.current_step] ?? run.current_step;

  return (
    <div className="rounded-lg border border-border">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left transition-colors hover:bg-muted/40"
      >
        <div className="flex min-w-0 items-center gap-3">
          <ChevronDown className={`h-4 w-4 shrink-0 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`} />
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <p className="font-medium">{meta.label}</p>
              <StatusBadge status={run.status} />
            </div>
            <p className="mt-0.5 truncate text-xs text-muted-foreground">
              {run.id.slice(0, 8)} · step <b>{stepLabel}</b> · started {timeAgo(run.created_at)}
            </p>
          </div>
        </div>
        {run.status === "awaiting_approval" && (
          <span className="flex shrink-0 items-center gap-1.5 rounded-full bg-warning/10 px-2.5 py-1 text-[11px] font-medium text-warning">
            <Activity className="h-3 w-3" /> Needs review
          </span>
        )}
      </button>

      {open && (
        <div className="space-y-4 border-t border-border px-4 py-4">
          <p className="text-sm text-muted-foreground">{meta.desc}</p>

          {run.status === "awaiting_approval" && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="mr-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Human checkpoint:
              </span>
              <Button size="sm" variant="outline" onClick={() => onResume(run, false)}>
                <X className="h-4 w-4" /> Reject draft
              </Button>
              <Button size="sm" onClick={() => onResume(run, true)}>
                <Check className="h-4 w-4" /> Approve & publish
              </Button>
            </div>
          )}

          <div className="grid gap-4 lg:grid-cols-3">
            <div>
              <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Input</p>
              <JsonBlock data={run.input_data} />
            </div>
            <div>
              <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Checkpoint</p>
              <JsonBlock data={run.checkpoint} />
            </div>
            <div>
              <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Output</p>
              <JsonBlock data={run.output_data} />
            </div>
          </div>

          {run.error && (
            <p className="rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-destructive">
              {run.error}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default function FlowsPage() {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [runs, setRuns] = useState<FlowRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [actingId, setActingId] = useState<string | null>(null);

  const slug = activeWorkspace?.slug;

  const refresh = useCallback(async () => {
    if (!slug) return;
    const data = await apiFetch<FlowRun[]>(`/api/v1/workspaces/${slug}/flows`);
    setRuns(data);
  }, [slug]);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    refresh()
      .catch(() => toast({ title: "Could not load flow runs", variant: "error" }))
      .finally(() => setLoading(false));
  }, [slug, refresh, toast]);

  const resume = async (run: FlowRun, approved: boolean) => {
    if (!slug) return;
    setActingId(run.id);
    try {
      await apiFetch<FlowRun>(`/api/v1/workspaces/${slug}/flows/${run.id}/resume`, {
        method: "POST",
        body: JSON.stringify({ approved }),
      });
      toast({
        title: approved ? "Draft approved & published" : "Draft rejected",
        variant: "success",
      });
      await refresh();
    } catch {
      toast({ title: "Could not resume flow", variant: "error" });
    } finally {
      setActingId(null);
    }
  };

  const counts = runs.reduce<Record<string, number>>((acc, r) => {
    acc[r.flow_key] = (acc[r.flow_key] ?? 0) + 1;
    return acc;
  }, {});

  const visible = filter === "all" ? runs : runs.filter((r) => r.flow_key === filter);
  const awaiting = runs.filter((r) => r.status === "awaiting_approval").length;

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <GitBranch className="h-5 w-5 text-primary" /> Workflow runs
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Checkpointed, resumable workflows. {awaiting} run{awaiting === 1 ? "" : "s"} currently awaiting a human
          decision.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          size="sm"
          variant={filter === "all" ? "default" : "outline"}
          onClick={() => setFilter("all")}
          className="gap-1.5"
        >
          All <span className="text-xs opacity-60">{runs.length}</span>
        </Button>
        {Object.entries(FLOW_LABELS).map(([key, meta]) => (
          <Button
            key={key}
            size="sm"
            variant={filter === key ? "default" : "outline"}
            onClick={() => setFilter(key)}
            className="gap-1.5"
          >
            {meta.label} <span className="text-xs opacity-60">{counts[key] ?? 0}</span>
          </Button>
        ))}
      </div>

      {visible.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center gap-2 py-12 text-center">
            <Activity className="h-10 w-10 text-muted-foreground/40" />
            <p className="text-sm font-medium">No workflow runs yet</p>
            <p className="max-w-md text-xs text-muted-foreground">
              Handle a ticket with AI to start a <b>ticket triage</b> run. Escalation and feedback runs are
              triggered from ticket flows.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {visible.map((run) => (
            <RunCard key={run.id} run={run} onResume={resume} />
          ))}
        </div>
      )}

      {actingId && (
        <p className="flex items-center gap-2 text-sm text-muted-foreground">
          <RotateCcw className="h-4 w-4 animate-spin" /> Resuming flow…
        </p>
      )}
    </div>
  );
}
