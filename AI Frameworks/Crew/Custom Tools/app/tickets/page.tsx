"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  Bot,
  Check,
  Inbox,
  MessageSquare,
  Plus,
  Send,
  Sparkles,
  ThumbsDown,
  X,
} from "lucide-react";

import {
  apiFetch,
  type FlowRun,
  type Ticket,
  type TicketDetail,
  type TicketHandleResult,
  type TicketMessage,
} from "@/lib/api";
import { useSession } from "@/lib/session";
import { timeAgo } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Modal } from "@/components/ui/modal";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { StatusBadge } from "@/components/ui/status-badge";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/toast";

const FILTERS: { key: string; label: string }[] = [
  { key: "all", label: "All" },
  { key: "new", label: "New" },
  { key: "open", label: "Open" },
  { key: "pending", label: "Pending" },
  { key: "resolved", label: "Resolved" },
  { key: "closed", label: "Closed" },
  { key: "escalated", label: "Escalated" },
];

function MessageBubble({ msg }: { msg: TicketMessage }) {
  const isUser = msg.sender === "user";
  const isAi = msg.sender === "ai";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
          isUser
            ? "rounded-br-sm bg-primary text-primary-foreground"
            : isAi
              ? "rounded-bl-sm border border-border bg-card"
              : "rounded-bl-sm bg-muted/60 text-muted-foreground"
        }`}
      >
        {isAi && (
          <p className="mb-1 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-primary">
            <Bot className="h-3 w-3" /> AI Support Crew
          </p>
        )}
        {isUser && msg.sender_name && (
          <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider opacity-70">{msg.sender_name}</p>
        )}
        <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
        <p className={`mt-1 text-right text-[10px] ${isUser ? "text-primary-foreground/60" : "text-muted-foreground"}`}>
          {new Date(msg.created_at).toLocaleString()}
        </p>
      </div>
    </div>
  );
}

export default function TicketsPage() {
  const { activeWorkspace, user } = useSession();
  const { toast } = useToast();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<TicketDetail | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [priority, setPriority] = useState("medium");
  const [creating, setCreating] = useState(false);
  const [handling, setHandling] = useState(false);
  const [handleResult, setHandleResult] = useState<TicketHandleResult | null>(null);
  const [acting, setActing] = useState(false);
  const [reply, setReply] = useState("");
  const [sending, setSending] = useState(false);

  const slug = activeWorkspace?.slug;

  const loadTickets = useCallback(async () => {
    if (!slug) return;
    const data = await apiFetch<Ticket[]>(`/api/v1/workspaces/${slug}/tickets`);
    setTickets(data);
  }, [slug]);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    loadTickets()
      .catch(() => toast({ title: "Could not load tickets", variant: "error" }))
      .finally(() => setLoading(false));
  }, [slug, loadTickets, toast]);

  const openTicket = async (ticket: Ticket) => {
    if (!slug) return;
    const detail = await apiFetch<TicketDetail>(`/api/v1/workspaces/${slug}/tickets/${ticket.id}`);
    setSelected(detail);
    setHandleResult(null);
  };

  const refreshSelected = async (id: string) => {
    if (!slug) return;
    const detail = await apiFetch<TicketDetail>(`/api/v1/workspaces/${slug}/tickets/${id}`);
    setSelected(detail);
    await loadTickets();
  };

  const createTicket = async () => {
    if (!slug) return;
    setCreating(true);
    try {
      const created = await apiFetch<TicketDetail>(`/api/v1/workspaces/${slug}/tickets`, {
        method: "POST",
        body: JSON.stringify({ subject, body, priority }),
      });
      toast({ title: "Ticket created", variant: "success" });
      setCreateOpen(false);
      setSubject("");
      setBody("");
      setPriority("medium");
      await loadTickets();
      await openTicket(created);
    } catch (error) {
      toast({
        title: "Could not create ticket",
        description: error instanceof Error ? error.message : undefined,
        variant: "error",
      });
    } finally {
      setCreating(false);
    }
  };

  const handleWithAI = async () => {
    if (!slug || !selected) return;
    setHandling(true);
    setHandleResult(null);
    try {
      const result = await apiFetch<TicketHandleResult>(
        `/api/v1/workspaces/${slug}/tickets/${selected.id}/ai-handle`,
        { method: "POST" },
      );
      setHandleResult(result);
      if (result.awaiting_approval) {
        toast({
          title: "Draft ready — waiting for your approval",
          description: "Urgent/escalation responses are gated behind a human checkpoint.",
        });
      } else {
        toast({ title: "Ticket resolved", variant: "success" });
      }
      await refreshSelected(selected.id);
    } catch (error) {
      toast({
        title: "AI handling failed",
        description: error instanceof Error ? error.message : undefined,
        variant: "error",
      });
    } finally {
      setHandling(false);
    }
  };

  const approve = async () => {
    if (!slug || !selected || !handleResult?.flow_run) return;
    setActing(true);
    try {
      await apiFetch(
        `/api/v1/workspaces/${slug}/flows/${handleResult.flow_run.id}/resume`,
        { method: "POST", body: JSON.stringify({ approved: true }) },
      );
      toast({ title: "Approved — AI draft published", variant: "success" });
      setHandleResult(null);
      await refreshSelected(selected.id);
    } catch {
      toast({ title: "Could not approve", variant: "error" });
    } finally {
      setActing(false);
    }
  };

  const reject = async () => {
    if (!slug || !selected || !handleResult?.flow_run) return;
    setActing(true);
    try {
      await apiFetch(
        `/api/v1/workspaces/${slug}/flows/${handleResult.flow_run.id}/resume`,
        { method: "POST", body: JSON.stringify({ approved: false }) },
      );
      toast({ title: "Draft rejected", variant: "success" });
      setHandleResult(null);
      await refreshSelected(selected.id);
    } catch {
      toast({ title: "Could not reject", variant: "error" });
    } finally {
      setActing(false);
    }
  };

  const sendReply = async () => {
    if (!slug || !selected || !reply.trim()) return;
    setSending(true);
    try {
      await apiFetch<TicketMessage>(
        `/api/v1/workspaces/${slug}/tickets/${selected.id}/messages`,
        { method: "POST", body: JSON.stringify({ content: reply.trim() }) },
      );
      setReply("");
      toast({ title: "Reply sent", variant: "success" });
      await refreshSelected(selected.id);
    } catch (error) {
      toast({
        title: "Could not send reply",
        description: error instanceof Error ? error.message : undefined,
        variant: "error",
      });
    } finally {
      setSending(false);
    }
  };

  const visible = filter === "all" ? tickets : tickets.filter((t) => t.status === filter);

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-72 w-full" />
      </div>
    );
  }

  if (selected) {
    const lastFlow: FlowRun | null = handleResult?.flow_run ?? null;
    return (
      <div className="space-y-5">
        <button
          onClick={() => setSelected(null)}
          className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" /> Back to tickets
        </button>

        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl font-semibold tracking-tight">{selected.subject}</h1>
              <StatusBadge status={selected.status} />
              <StatusBadge status={selected.priority} />
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              {selected.classification ? `Classified as ${selected.classification} · ` : ""}
              created {timeAgo(selected.created_at)} · {selected.message_count} message
              {selected.message_count === 1 ? "" : "s"}
            </p>
          </div>
          {selected.status !== "resolved" && selected.status !== "closed" && (
            <Button onClick={handleWithAI} disabled={handling}>
              {handling ? <Spinner /> : <Sparkles className="h-4 w-4" />}
              {handling ? "Working…" : "Handle with AI"}
            </Button>
          )}
        </div>

        {selected.ai_summary && (
          <div className="rounded-lg border border-primary/20 bg-primary/5 p-3 text-sm">
            <p className="mb-1 text-xs font-semibold text-primary">AI summary</p>
            <p className="text-muted-foreground">{selected.ai_summary}</p>
          </div>
        )}

        {handleResult && handleResult.awaiting_approval && (
          <Card className="border-warning/40">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <ThumbsDown className="h-4 w-4 text-warning" /> Human approval checkpoint
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="rounded-lg border border-border bg-muted/30 p-4">
                <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  <Bot className="h-3.5 w-3.5 text-primary" /> Proposed AI reply
                </p>
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{handleResult.draft}</p>
              </div>
              {handleResult.sources.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Knowledge sources used
                  </p>
                  <div className="space-y-1.5">
                    {handleResult.sources.map((s, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs">
                        <span className="rounded-full bg-primary/10 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
                          {Math.round(s.score * 100)}%
                        </span>
                        <span className="truncate text-muted-foreground">{s.filename}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={reject} disabled={acting}>
                  {acting ? <Spinner /> : <X className="h-4 w-4" />} Reject draft
                </Button>
                <Button onClick={approve} disabled={acting}>
                  {acting ? <Spinner /> : <Check className="h-4 w-4" />} Approve & send
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {lastFlow && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>Flow run {lastFlow.id.slice(0, 8)}</span>
            <StatusBadge status={lastFlow.status} />
            {handleResult?.engine && <span>· engine: {handleResult.engine}</span>}
          </div>
        )}

        <Card>
          <CardContent className="space-y-3 pt-6">
            <div className="flex items-center gap-2 pb-1">
              <MessageSquare className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">Conversation</span>
            </div>
            {selected.messages.length === 0 ? (
              <p className="text-sm text-muted-foreground">No messages yet.</p>
            ) : (
              selected.messages.map((msg) => <MessageBubble key={msg.id} msg={msg} />)
            )}
          </CardContent>
        </Card>

        <div className="flex gap-2">
          <Textarea
            value={reply}
            onChange={(e) => setReply(e.target.value)}
            placeholder="Write a reply to the customer…"
            rows={3}
            className="resize-none"
          />
          <Button onClick={sendReply} disabled={sending || !reply.trim()}>
            {sending ? <Spinner /> : <Send className="h-4 w-4" />}
            Send
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Tickets</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {tickets.length} total · {tickets.filter((t) => t.status === "new").length} new
          </p>
        </div>
        <Button size="sm" onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" /> New ticket
        </Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => {
          const count = f.key === "all" ? tickets.length : tickets.filter((t) => t.status === f.key).length;
          return (
            <Button
              key={f.key}
              size="sm"
              variant={filter === f.key ? "default" : "outline"}
              onClick={() => setFilter(f.key)}
              className="gap-1.5"
            >
              {f.label}
              <span className="text-xs opacity-60">{count}</span>
            </Button>
          );
        })}
      </div>

      <Card>
        <CardContent className="p-0">
          {visible.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-12 text-center">
              <Inbox className="h-10 w-10 text-muted-foreground/40" />
              <p className="text-sm font-medium">No tickets here</p>
              <p className="max-w-sm text-xs text-muted-foreground">
                Create a ticket to see the AI support crew in action — or change the filter above.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-border">
              {visible.map((t) => (
                <button
                  key={t.id}
                  onClick={() => openTicket(t)}
                  className="flex w-full items-start justify-between gap-4 px-5 py-4 text-left transition-colors hover:bg-muted/40"
                >
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="truncate font-medium">{t.subject}</p>
                      <StatusBadge status={t.status} />
                      <StatusBadge status={t.priority} />
                    </div>
                    <p className="mt-1 line-clamp-1 text-sm text-muted-foreground">{t.body}</p>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-1">
                    <span className="text-xs text-muted-foreground">{timeAgo(t.created_at)}</span>
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                      <MessageSquare className="h-3 w-3" /> {t.message_count}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="New support ticket" description="The AI crew will classify it and draft a reply.">
        <div className="space-y-3">
          <Label htmlFor="t-subject">Subject</Label>
          <Input
            id="t-subject"
            placeholder="Billing issue"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
          <Label htmlFor="t-body">Description</Label>
          <Textarea
            id="t-body"
            rows={5}
            placeholder="What can we help with?"
            value={body}
            onChange={(e) => setBody(e.target.value)}
          />
          <Label>Priority</Label>
          <div className="flex gap-2">
            {["low", "medium", "high", "urgent"].map((p) => (
              <Button
                key={p}
                size="sm"
                type="button"
                variant={priority === p ? "default" : "outline"}
                className="capitalize"
                onClick={() => setPriority(p)}
              >
                {p}
              </Button>
            ))}
          </div>
          <div className="flex justify-end gap-2 pt-1">
            <Button variant="ghost" onClick={() => setCreateOpen(false)}>Cancel</Button>
            <Button onClick={createTicket} disabled={creating || !subject.trim() || !body.trim()}>
              {creating ? <Spinner /> : <Plus className="h-4 w-4" />} Create ticket
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
