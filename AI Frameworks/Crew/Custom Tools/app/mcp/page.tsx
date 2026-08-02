"use client";

import { useCallback, useEffect, useState } from "react";
import { Plug, Play } from "lucide-react";

import { apiFetch, type McpCallResult, type McpServer } from "@/lib/api";
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

function ServerCard({ server }: { server: McpServer }) {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [toolName, setToolName] = useState<string>(server.tools[0]?.name ?? "");
  const [args, setArgs] = useState<string>("{}");
  const [result, setResult] = useState<McpCallResult | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    if (!activeWorkspace || !toolName) return;
    setBusy(true);
    setResult(null);
    try {
      const parsed = JSON.parse(args || "{}");
      const res = await apiFetch<McpCallResult>(
        `/api/v1/workspaces/${activeWorkspace.slug}/mcp/call`,
        {
          method: "POST",
          body: JSON.stringify({ server_id: server.id, tool_name: toolName, arguments: parsed }),
        },
      );
      setResult(res);
      if (!res.success) toast({ title: "MCP call failed", description: res.error });
    } catch (err) {
      toast({ title: "MCP call failed", description: String(err) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="flex items-center gap-2 text-sm">
            <Plug className="h-4 w-4 text-primary" />
            {server.name}
          </CardTitle>
          <Badge variant="secondary">{server.tools.length} tools</Badge>
        </div>
        <CardDescription>
          {server.description ?? "Exposes tools your AI crew can call from within the workspace."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {server.resources.length > 0 && (
          <div className="space-y-2">
            <span className="block text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Resources
            </span>
            <div className="space-y-1.5">
              {server.resources.map((r) => (
                <div key={r.uri} className="rounded-md border border-border bg-muted/30 p-2 text-[11px]">
                  <p className="font-medium text-foreground">{r.name}</p>
                  <p className="text-muted-foreground">{r.description}</p>
                  <code className="block truncate text-[10px] text-muted-foreground">{r.uri}</code>
                </div>
              ))}
            </div>
          </div>
        )}
        <div className="space-y-2">
          <span className="block text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Available tools
          </span>
          <div className="flex flex-wrap gap-1.5">
            {server.tools.map((t) => (
              <button
                key={t.name}
                onClick={() => {
                  setToolName(t.name);
                  setResult(null);
                }}
                className={`rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors ${
                  toolName === t.name
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/70"
                }`}
                title={t.description}
              >
                {t.name}
              </button>
            ))}
          </div>
        </div>

        <label className="block">
          <span className="mb-1 block text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Arguments (JSON)
          </span>
          <textarea
            value={args}
            onChange={(e) => setArgs(e.target.value)}
            spellCheck={false}
            className="min-h-20 w-full resize-y rounded-md border bg-muted/30 p-3 font-mono text-xs"
          />
        </label>

        <Button size="sm" onClick={run} disabled={busy || !activeWorkspace || !toolName}>
          <Play className="h-3.5 w-3.5" /> {busy ? "Calling…" : "Call tool"}
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

export default function McpPage() {
  const { activeWorkspace } = useSession();
  const [servers, setServers] = useState<McpServer[] | null>(null);

  const load = useCallback(async () => {
    if (!activeWorkspace) return;
    setServers(
      await apiFetch<McpServer[]>(`/api/v1/workspaces/${activeWorkspace.slug}/mcp/servers`),
    );
  }, [activeWorkspace]);

  useEffect(() => {
    load().catch(() => setServers([]));
  }, [load]);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Plug className="h-6 w-6 text-primary" /> Model Context Protocol
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Registered MCP servers — filesystem, GitHub and browser — expose resources and tools
          your AI crew can call from within the workspace.
        </p>
      </div>

      {!servers ? (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-72 w-full" />
          <Skeleton className="h-72 w-full" />
          <Skeleton className="h-72 w-full" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {servers.map((server) => (
            <ServerCard key={server.id} server={server} />
          ))}
        </div>
      )}
    </div>
  );
}
