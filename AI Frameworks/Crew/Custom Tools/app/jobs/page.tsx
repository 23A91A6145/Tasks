"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Download,
  FileText,
  Globe,
  Hammer,
  ListChecks,
  Plus,
  RotateCcw,
  Trash2,
} from "lucide-react";

import {
  apiFetch,
  type Job,
  type KnowledgeDocument,
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
import { useToast } from "@/components/ui/toast";

const JOB_TYPES = [
  { key: "index_document", label: "Re-index document", icon: FileText, desc: "Rebuild chunks for a document" },
  { key: "crawl_website", label: "Crawl website", icon: Globe, desc: "Index pages from a URL" },
  { key: "batch_faq", label: "Batch FAQ", icon: ListChecks, desc: "Ingest a FAQ entry" },
  { key: "weekly_report", label: "Weekly report", icon: Download, desc: "Generate an AI usage report" },
];

function JobRow({
  job,
  onRetry,
  onDelete,
  acting,
}: {
  job: Job;
  onRetry: (job: Job) => void;
  onDelete: (job: Job) => void;
  acting: boolean;
}) {
  const running = job.status === "running" || job.status === "queued";
  const failed = job.status === "failed";
  return (
    <div className="border-b border-border px-5 py-4 last:border-0">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
            <Hammer className="h-4 w-4 text-primary" />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <p className="font-medium">{job.label ?? job.job_type}</p>
              <StatusBadge status={job.status} />
            </div>
            <p className="mt-0.5 text-xs text-muted-foreground">
              <span className="capitalize">{job.job_type}</span> · {job.id.slice(0, 8)} ·{" "}
              {job.started_at ? `started ${timeAgo(job.started_at)}` : `created ${timeAgo(job.created_at)}`}
              {job.finished_at ? ` · finished ${timeAgo(job.finished_at)}` : ""}
            </p>
            {job.current_step && (
              <p className="mt-0.5 text-xs text-muted-foreground">step: {job.current_step}</p>
            )}
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          {failed && (
            <Button size="sm" variant="outline" disabled={acting} onClick={() => onRetry(job)}>
              <RotateCcw className="h-3.5 w-3.5" /> Retry
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            disabled={acting}
            onClick={() => onDelete(job)}
            className="text-muted-foreground hover:text-destructive"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      <div className="mt-3 flex items-center gap-3">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
          <div
            className={`h-full rounded-full transition-all ${
              failed ? "bg-destructive" : running ? "bg-primary animate-pulse" : "bg-success"
            }`}
            style={{ width: `${Math.max(job.progress, job.status === "queued" ? 2 : 0)}%` }}
          />
        </div>
        <span className="w-10 text-right text-xs tabular-nums text-muted-foreground">
          {job.progress}%
        </span>
      </div>

      {job.error && (
        <p className="mt-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-xs text-destructive">
          {job.error}
        </p>
      )}
    </div>
  );
}

export default function JobsPage() {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);

  const [jobType, setJobType] = useState("crawl_website");
  const [documentId, setDocumentId] = useState("");
  const [url, setUrl] = useState("");
  const [maxPages, setMaxPages] = useState(10);
  const [name, setName] = useState("");
  const [content, setContent] = useState("");
  const [label, setLabel] = useState("");
  const [creating, setCreating] = useState(false);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);

  const slug = activeWorkspace?.slug;

  const refresh = useCallback(async () => {
    if (!slug) return;
    const data = await apiFetch<Job[]>(`/api/v1/workspaces/${slug}/jobs`);
    setJobs(data);
  }, [slug]);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    refresh()
      .catch(() => toast({ title: "Could not load jobs", variant: "error" }))
      .finally(() => setLoading(false));
  }, [slug, refresh, toast]);

  useEffect(() => {
    if (!slug || jobType !== "index_document") return;
    apiFetch<KnowledgeDocument[]>(`/api/v1/workspaces/${slug}/knowledge`)
      .then((docs) => setDocuments(docs))
      .catch(() => setDocuments([]));
  }, [slug, jobType]);

  const openCreate = () => {
    setJobType("crawl_website");
    setDocumentId("");
    setUrl("");
    setMaxPages(10);
    setName("");
    setContent("");
    setLabel("");
    setCreateOpen(true);
  };

  const createJob = async () => {
    if (!slug) return;
    setCreating(true);
    try {
      const body: Record<string, unknown> = { job_type: jobType };
      if (label.trim()) body.label = label.trim();
      if (jobType === "index_document") {
        if (!documentId) throw new Error("Pick a document to re-index");
        body.document_id = documentId;
      } else if (jobType === "crawl_website") {
        if (!url.trim()) throw new Error("Enter a URL to crawl");
        body.url = url.trim();
        body.max_pages = maxPages;
      } else if (jobType === "batch_faq") {
        if (!name.trim() || !content.trim()) throw new Error("FAQ needs a question and an answer");
        body.name = name.trim();
        body.content = content.trim();
      }
      await apiFetch<Job>(`/api/v1/workspaces/${slug}/jobs`, {
        method: "POST",
        body: JSON.stringify(body),
      });
      toast({ title: "Job created", variant: "success" });
      setCreateOpen(false);
      await refresh();
    } catch (error) {
      toast({
        title: "Could not create job",
        description: error instanceof Error ? error.message : undefined,
        variant: "error",
      });
    } finally {
      setCreating(false);
    }
  };

  const retry = async (job: Job) => {
    if (!slug) return;
    setActing(true);
    try {
      await apiFetch<Job>(`/api/v1/workspaces/${slug}/jobs/${job.id}/retry`, { method: "POST" });
      toast({ title: "Job retried", variant: "success" });
      await refresh();
    } catch {
      toast({ title: "Could not retry job", variant: "error" });
    } finally {
      setActing(false);
    }
  };

  const remove = async (job: Job) => {
    if (!slug) return;
    setActing(true);
    try {
      await apiFetch<void>(`/api/v1/workspaces/${slug}/jobs/${job.id}`, { method: "DELETE" });
      toast({ title: "Job deleted", variant: "success" });
      await refresh();
    } catch {
      toast({ title: "Could not delete job", variant: "error" });
    } finally {
      setActing(false);
    }
  };

  const counts = jobs.reduce<Record<string, number>>((acc, j) => {
    acc[j.job_type] = (acc[j.job_type] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
            <Hammer className="h-5 w-5 text-primary" /> Jobs
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Long-running tasks with progress, checkpoints and retry. {jobs.length} total.
          </p>
        </div>
        <Button size="sm" onClick={openCreate}>
          <Plus className="h-4 w-4" /> New job
        </Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {JOB_TYPES.map((jt) => (
          <span
            key={jt.key}
            className="flex items-center gap-1.5 rounded-md border border-border bg-card px-2.5 py-1.5 text-xs text-muted-foreground"
          >
            <jt.icon className="h-3.5 w-3.5" />
            {jt.label}
            <Badge variant="secondary" className="px-1.5 text-[10px]">
              {counts[jt.key] ?? 0}
            </Badge>
          </span>
        ))}
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="space-y-4 p-5">
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </div>
          ) : jobs.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-12 text-center">
              <Hammer className="h-10 w-10 text-muted-foreground/40" />
              <p className="text-sm font-medium">No jobs yet</p>
              <p className="max-w-sm text-xs text-muted-foreground">
                Re-index a document, crawl a website, import an FAQ or generate a weekly report.
              </p>
            </div>
          ) : (
            jobs.map((job) => (
              <JobRow key={job.id} job={job} onRetry={retry} onDelete={remove} acting={acting} />
            ))
          )}
        </CardContent>
      </Card>

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="New job" description="Jobs run in the background with progress tracking.">
        <div className="space-y-4">
          <div>
            <Label>Job type</Label>
            <div className="mt-2 grid gap-2 sm:grid-cols-2">
              {JOB_TYPES.map((jt) => (
                <button
                  key={jt.key}
                  type="button"
                  onClick={() => setJobType(jt.key)}
                  className={`rounded-lg border p-3 text-left transition-colors ${
                    jobType === jt.key
                      ? "border-primary bg-primary/5"
                      : "border-border hover:bg-muted/40"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <jt.icon className="h-4 w-4 text-primary" />
                    <span className="text-sm font-medium">{jt.label}</span>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{jt.desc}</p>
                </button>
              ))}
            </div>
          </div>

          <div>
            <Label htmlFor="j-label">Label (optional)</Label>
            <Input
              id="j-label"
              className="mt-1.5"
              placeholder="e.g. Rebuild product docs index"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
            />
          </div>

          {jobType === "index_document" && (
            <div>
              <Label htmlFor="j-doc">Document</Label>
              <select
                id="j-doc"
                className="mt-1.5 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={documentId}
                onChange={(e) => setDocumentId(e.target.value)}
              >
                <option value="">Select a document…</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.filename}
                  </option>
                ))}
              </select>
            </div>
          )}

          {jobType === "crawl_website" && (
            <div className="space-y-3">
              <div>
                <Label htmlFor="j-url">Website URL</Label>
                <Input
                  id="j-url"
                  className="mt-1.5"
                  placeholder="https://example.com/docs"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="j-pages">Max pages</Label>
                <Input
                  id="j-pages"
                  className="mt-1.5"
                  type="number"
                  min={1}
                  max={50}
                  value={maxPages}
                  onChange={(e) => setMaxPages(Number(e.target.value))}
                />
              </div>
            </div>
          )}

          {jobType === "batch_faq" && (
            <div className="space-y-3">
              <div>
                <Label htmlFor="j-faq-name">Question</Label>
                <Input
                  id="j-faq-name"
                  className="mt-1.5"
                  placeholder="How do I reset my password?"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="j-faq-content">Answer</Label>
                <textarea
                  id="j-faq-content"
                  rows={3}
                  className="mt-1.5 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  placeholder="Go to Settings → Security → Reset password…"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                />
              </div>
            </div>
          )}

          {jobType === "weekly_report" && (
            <p className="rounded-md border border-border bg-muted/40 px-3 py-2 text-xs text-muted-foreground">
              Generates a Markdown summary of your AI usage for the last 7 days.
            </p>
          )}

          <div className="flex justify-end gap-2 pt-1">
            <Button variant="ghost" onClick={() => setCreateOpen(false)}>
              Cancel
            </Button>
            <Button onClick={createJob} disabled={creating}>
              {creating ? <Spinner /> : <Hammer className="h-4 w-4" />} Run job
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
