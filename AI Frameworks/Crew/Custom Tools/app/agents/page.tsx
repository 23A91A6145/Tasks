"use client";

import { useCallback, useEffect, useState } from "react";
import { Bot, Cpu, Database, KeyRound, Pencil, Save, X } from "lucide-react";

import { apiFetch, type AgentConfig, type EngineStatus } from "@/lib/api";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

const ENGINE_META: Record<string, { label: string; desc: string }> = {
  crewai: {
    label: "CrewAI hierarchical crew",
    desc: "A manager delegates to specialist agents — the full production setup.",
  },
  llm: {
    label: "Direct LLM",
    desc: "One LLM call, no crew. Picked when CrewAI isn't installed or has no key.",
  },
  fallback: {
    label: "Rule engine",
    desc: "Deterministic, offline and free — always works, no API key needed.",
  },
};

function EngineCard({ status }: { status: EngineStatus }) {
  const meta = ENGINE_META[status.engine] ?? { label: status.engine, desc: "" };
  return (
    <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Cpu className="h-4 w-4 text-primary" /> Active AI engine
          <Badge variant="outline" className="text-primary">{status.engine}</Badge>
        </CardTitle>
        <CardDescription>{meta.desc}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="flex items-start gap-2 rounded-lg bg-card p-3">
            <Bot className="mt-0.5 h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs font-medium">CrewAI</p>
              <p className="text-xs text-muted-foreground">
                {status.crewai_available ? "Installed — hierarchical crew available" : "Not installed (optional)"}
              </p>
            </div>
          </div>
          <div className="flex items-start gap-2 rounded-lg bg-card p-3">
            <KeyRound className="mt-0.5 h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs font-medium">LLM provider</p>
              <p className="text-xs text-muted-foreground">
                {status.llm_configured
                  ? `${status.llm_provider} · ${status.llm_model}`
                  : "None configured — using offline rules"}
              </p>
            </div>
          </div>
          <div className="flex items-start gap-2 rounded-lg bg-card p-3">
            <Database className="mt-0.5 h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs font-medium">Embeddings</p>
              <p className="text-xs text-muted-foreground">{status.embeddings_provider}</p>
            </div>
          </div>
          <div className="flex items-start gap-2 rounded-lg bg-card p-3">
            <Database className="mt-0.5 h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs font-medium">Vector store</p>
              <p className="text-xs text-muted-foreground">{status.vector_store}</p>
            </div>
          </div>
        </div>
        {status.notes && (
          <p className="mt-3 rounded-md bg-muted/60 p-2.5 text-xs text-muted-foreground">{status.notes}</p>
        )}
      </CardContent>
    </Card>
  );
}

function AgentRow({ agent, slug, onUpdate }: { agent: AgentConfig; slug: string; onUpdate: (a: AgentConfig) => Promise<void> }) {
  const [editing, setEditing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [name, setName] = useState(agent.name);
  const [role, setRole] = useState(agent.role_description ?? "");
  const [model, setModel] = useState(agent.llm_model ?? "");
  const { toast } = useToast();

  const toggle = async () => {
    setBusy(true);
    try {
      const updated = await apiFetch<AgentConfig>(
        `/api/v1/workspaces/${slug}/agents/${agent.key}`,
        {
          method: "PATCH",
          body: JSON.stringify({ enabled: !agent.enabled }),
        },
      );
      await onUpdate(updated);
    } catch {
      toast({ title: "Could not update agent", variant: "error" });
    } finally {
      setBusy(false);
    }
  };

  const save = async () => {
    setBusy(true);
    try {
      const updated = await apiFetch<AgentConfig>(
        `/api/v1/workspaces/${slug}/agents/${agent.key}`,
        {
          method: "PATCH",
          body: JSON.stringify({ name, role_description: role, llm_model: model || null }),
        },
      );
      setEditing(false);
      await onUpdate(updated);
    } catch {
      toast({ title: "Could not save agent", variant: "error" });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className={`rounded-lg border p-4 transition-opacity ${agent.enabled ? "border-border" : "border-border/50 opacity-60"}`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
            <Bot className="h-[18px] w-[18px] text-primary" />
          </div>
          <div className="min-w-0">
            {editing ? (
              <Input value={name} onChange={(e) => setName(e.target.value)} className="mb-1 max-w-xs" />
            ) : (
              <p className="font-medium">{agent.name}</p>
            )}
            <p className="text-xs text-muted-foreground">
              {editing
                ? `Editing ${agent.key}`
                : agent.enabled
                  ? "Active in the crew"
                  : "Disabled — excluded from the crew"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          {agent.llm_model && !editing && <Badge variant="secondary">{agent.llm_model}</Badge>}
          <Button
            variant="outline"
            size="icon"
            title={editing ? "Close" : "Edit"}
            onClick={() => (editing ? setEditing(false) : setEditing(true))}
          >
            {editing ? <X className="h-4 w-4" /> : <Pencil className="h-4 w-4" />}
          </Button>
          <Button variant="outline" size="sm" onClick={toggle} disabled={busy}>
            {busy ? <Spinner /> : agent.enabled ? "Disable" : "Enable"}
          </Button>
        </div>
      </div>

      <p className="mt-2 text-sm text-muted-foreground">
        {editing ? (
          <div className="mt-2 space-y-3">
            <div>
              <Label>Role description</Label>
              <Input value={role} onChange={(e) => setRole(e.target.value)} className="mt-1" placeholder="What this agent does" />
            </div>
            <div>
              <Label>LLM model override</Label>
              <Input value={model} onChange={(e) => setModel(e.target.value)} className="mt-1" placeholder="Optional, e.g. gpt-4o-mini" />
            </div>
            <Button size="sm" onClick={save} disabled={busy || !name.trim()}>
              {busy ? <Spinner /> : <Save className="h-4 w-4" />} Save
            </Button>
          </div>
        ) : (
          agent.role_description
        )}
      </p>
    </div>
  );
}

export default function AgentsPage() {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [agents, setAgents] = useState<AgentConfig[]>([]);
  const [engine, setEngine] = useState<EngineStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const slug = activeWorkspace?.slug;

  const refresh = useCallback(async () => {
    if (!slug) return;
    const [agentData, engineData] = await Promise.all([
      apiFetch<AgentConfig[]>(`/api/v1/workspaces/${slug}/agents`),
      apiFetch<EngineStatus>(`/api/v1/workspaces/${slug}/agents/engine`),
    ]);
    setAgents(agentData);
    setEngine(engineData);
  }, [slug]);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    refresh()
      .catch(() => toast({ title: "Could not load agents", variant: "error" }))
      .finally(() => setLoading(false));
  }, [slug, refresh, toast]);

  const updateAgent = async (updated: AgentConfig) => {
    setAgents((prev) => prev.map((a) => (a.key === updated.key ? updated : a)));
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-52 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <Bot className="h-5 w-5 text-primary" /> AI agents
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Your per-workspace support crew — configured per tenant, isolated from every other workspace.
        </p>
      </div>

      {engine && <EngineCard status={engine} />}

      <div className="space-y-3">
        {agents.map((agent) => (
          <AgentRow key={agent.key} agent={agent} slug={slug ?? ""} onUpdate={updateAgent} />
        ))}
      </div>
    </div>
  );
}
