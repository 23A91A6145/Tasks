"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Play, Wrench } from "lucide-react";

import { apiFetch, type ToolDefinition, type ToolResult } from "@/lib/api";
import { useSession } from "@/lib/session";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/toast";

const EXAMPLES: Record<string, Record<string, string>> = {
  calculator: { expression: "150 * 0.85" },
  web_search: { query: "billing price plans" },
  crm_lookup: { customer_email: "alice@company.com" },
  send_email: { recipient: "customer@example.com", subject: "Ticket Resolved", body: "All set." },
  schedule_calendar: { title: "Onboarding", attendee_email: "bob@tenant.com", date_time: "2026-08-01 10:00 UTC" },
  github_tool: { action: "create_issue", repo: "acme/support", title: "Bug in auth flow" },
};

function ToolCard({ tool }: { tool: ToolDefinition }) {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [args, setArgs] = useState<string>(
    JSON.stringify(EXAMPLES[tool.name] ?? {}, null, 2),
  );
  const [result, setResult] = useState<ToolResult | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    if (!activeWorkspace) return;
    setBusy(true);
    setResult(null);
    try {
      const parsed = JSON.parse(args || "{}");
      const res = await apiFetch<ToolResult>(
        `/api/v1/workspaces/${activeWorkspace.slug}/tools/execute`,
        { method: "POST", body: JSON.stringify({ tool_name: tool.name, arguments: parsed }) },
      );
      setResult(res);
      if (!res.success) toast({ title: "Tool failed", description: res.error });
    } catch (err) {
      toast({ title: "Execution failed", description: String(err) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="font-mono text-sm">{tool.name}</CardTitle>
          <Badge variant="secondary">{tool.category}</Badge>
        </div>
        <CardDescription>{tool.description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <label className="block">
          <span className="mb-1 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Arguments (JSON)
          </span>
          <textarea
            value={args}
            onChange={(e) => setArgs(e.target.value)}
            spellCheck={false}
            className="min-h-24 w-full resize-y rounded-md border bg-muted/30 p-3 font-mono text-xs"
          />
        </label>
        <Button size="sm" onClick={run} disabled={busy || !activeWorkspace}>
          <Play className="h-3.5 w-3.5" /> {busy ? "Running…" : "Execute"}
        </Button>
        {result && (
          <pre className="max-h-56 overflow-auto rounded-md bg-muted/50 p-3 text-[11px] leading-relaxed text-muted-foreground">
            {JSON.stringify(result, null, 2)}
          </pre>
        )}
      </CardContent>
    </Card>
  );
}

export default function ToolsPage() {
  const { activeWorkspace } = useSession();
  const [tools, setTools] = useState<ToolDefinition[] | null>(null);
  const [category, setCategory] = useState<string>("all");

  const load = useCallback(async () => {
    if (!activeWorkspace) return;
    setTools(
      await apiFetch<ToolDefinition[]>(
        `/api/v1/workspaces/${activeWorkspace.slug}/tools${
          category !== "all" ? `?category=${category}` : ""
        }`,
      ),
    );
  }, [activeWorkspace, category]);

  useEffect(() => {
    load().catch(() => setTools([]));
  }, [load]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    tools?.forEach((t) => set.add(t.category));
    return ["all", ...set];
  }, [tools]);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Wrench className="h-6 w-6 text-primary" /> Tool Ecosystem
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Built-in tools your AI agents can use — calculator, CRM lookup, web search, email,
          calendar and GitHub. Pick one and try it with JSON arguments.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {categories.map((c) => (
          <button
            key={c}
            onClick={() => setCategory(c)}
            className={`rounded-full px-3 py-1 text-xs font-medium capitalize transition-colors ${
              category === c
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground hover:bg-muted/70"
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      {!tools ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      ) : tools.length === 0 ? (
        <p className="py-12 text-center text-sm text-muted-foreground">
          No tools in this category. Try another filter.
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {tools.map((tool) => (
            <ToolCard key={tool.name} tool={tool} />
          ))}
        </div>
      )}
    </div>
  );
}
