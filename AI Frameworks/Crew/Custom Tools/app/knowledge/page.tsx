"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  BookOpen,
  FileText,
  Globe,
  Link2,
  MessageCircleQuestion,
  NotebookPen,
  Plus,
  Search,
  Trash2,
  Upload,
} from "lucide-react";

import {
  apiFetch,
  apiUpload,
  formatBytes,
  type KnowledgeDocument,
  type KnowledgeHit,
  type KnowledgeSearchResult,
  type TagOut,
} from "@/lib/api";
import { useSession } from "@/lib/session";
import { timeAgo } from "@/lib/utils";
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
import { Modal } from "@/components/ui/modal";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { StatusBadge } from "@/components/ui/status-badge";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/toast";

const SOURCE_LABELS: Record<string, { label: string; icon: React.ComponentType<{ className?: string }> }> = {
  upload: { label: "Upload", icon: Upload },
  url: { label: "Website", icon: Globe },
  faq: { label: "FAQ", icon: MessageCircleQuestion },
};

function Progress({ value }: { value: number }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
      <div
        className="h-full rounded-full bg-primary transition-all duration-300"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}

function UploadZone({
  onFile,
  busy,
}: {
  onFile: (file: File) => void;
  busy: boolean;
}) {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <button
      type="button"
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        const file = e.dataTransfer.files?.[0];
        if (file) onFile(file);
      }}
      disabled={busy}
      className={`flex w-full cursor-pointer flex-col items-center gap-3 rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors ${
        drag ? "border-primary bg-primary/5" : "border-border hover:border-primary/40"
      } ${busy ? "pointer-events-none opacity-60" : ""}`}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
        {busy ? <Spinner className="h-6 w-6 text-primary" /> : <Upload className="h-6 w-6 text-primary" />}
      </div>
      <div>
        <p className="text-sm font-medium">Drop a document here or click to browse</p>
        <p className="mt-1 text-xs text-muted-foreground">
          PDF · DOCX · Markdown · TXT · CSV — up to 25 MB. Your tenant gets an isolated RAG namespace.
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept=".pdf,.docx,.md,.txt,.csv"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onFile(file);
          e.currentTarget.value = "";
        }}
      />
    </button>
  );
}

export default function KnowledgePage() {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [docs, setDocs] = useState<KnowledgeDocument[]>([]);
  const [tags, setTags] = useState<TagOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [query, setQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [results, setResults] = useState<KnowledgeHit[] | null>(null);
  const [urlOpen, setUrlOpen] = useState(false);
  const [faqOpen, setFaqOpen] = useState(false);
  const [textOpen, setTextOpen] = useState(false);
  const [url, setUrl] = useState("");
  const [faqName, setFaqName] = useState("");
  const [faqContent, setFaqContent] = useState("");
  const [textName, setTextName] = useState("");
  const [textContent, setTextContent] = useState("");

  const slug = activeWorkspace?.slug;

  const refresh = useCallback(async () => {
    if (!slug) return;
    const [docData, tagData] = await Promise.all([
      apiFetch<KnowledgeDocument[]>(`/api/v1/workspaces/${slug}/knowledge`),
      apiFetch<TagOut[]>(`/api/v1/workspaces/${slug}/knowledge/tags`),
    ]);
    setDocs(docData);
    setTags(tagData);
  }, [slug]);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    refresh().finally(() => setLoading(false));
  }, [slug, refresh]);

  const uploadFile = async (file: File) => {
    if (!slug) return;
    setUploading(true);
    setProgress(10);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("tags", "");
      await apiUpload<KnowledgeDocument>(
        `/api/v1/workspaces/${slug}/knowledge`,
        form,
        setProgress,
      );
      toast({ title: `${file.name} indexed`, variant: "success" });
      await refresh();
    } catch (error) {
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "Something went wrong",
        variant: "error",
      });
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const deleteDoc = async (doc: KnowledgeDocument) => {
    if (!slug) return;
    try {
      await apiFetch<void>(`/api/v1/workspaces/${slug}/knowledge/${doc.id}`, { method: "DELETE" });
      toast({ title: `${doc.filename} deleted`, variant: "success" });
      await refresh();
    } catch (error) {
      toast({ title: "Delete failed", variant: "error" });
    }
  };

  const search = async () => {
    if (!slug || !query.trim()) return;
    setSearching(true);
    try {
      const data = await apiFetch<KnowledgeSearchResult>(
        `/api/v1/workspaces/${slug}/knowledge/search`,
        {
          method: "POST",
          body: JSON.stringify({ query: query.trim(), top_k: 6 }),
        },
      );
      setResults(data.hits);
    } catch {
      toast({ title: "Search failed", variant: "error" });
    } finally {
      setSearching(false);
    }
  };

  const submitUrl = async () => {
    if (!slug || !url.trim()) return;
    try {
      await apiFetch<KnowledgeDocument>(`/api/v1/workspaces/${slug}/knowledge/ingest-url`, {
        method: "POST",
        body: JSON.stringify({ url: url.trim() }),
      });
      toast({ title: "Website ingested", variant: "success" });
      setUrl("");
      setUrlOpen(false);
      await refresh();
    } catch (error) {
      toast({
        title: "Could not ingest URL",
        description: error instanceof Error ? error.message : "Check the URL and network",
        variant: "error",
      });
    }
  };

  const submitFaq = async () => {
    if (!slug || !faqName.trim() || !faqContent.trim()) return;
    try {
      await apiFetch<KnowledgeDocument>(`/api/v1/workspaces/${slug}/knowledge/faq`, {
        method: "POST",
        body: JSON.stringify({ name: faqName.trim(), content: faqContent.trim() }),
      });
      toast({ title: "FAQ added to knowledge base", variant: "success" });
      setFaqName("");
      setFaqContent("");
      setFaqOpen(false);
      await refresh();
    } catch {
      toast({ title: "Could not add FAQ", variant: "error" });
    }
  };

  const submitText = async () => {
    if (!slug || !textName.trim() || !textContent.trim()) return;
    try {
      await apiFetch<KnowledgeDocument>(`/api/v1/workspaces/${slug}/knowledge/text`, {
        method: "POST",
        body: JSON.stringify({ name: textName.trim(), content: textContent.trim() }),
      });
      toast({ title: "Text added to knowledge base", variant: "success" });
      setTextName("");
      setTextContent("");
      setTextOpen(false);
      await refresh();
    } catch {
      toast({ title: "Could not add text", variant: "error" });
    }
  };

  const readyCount = docs.filter((d) => d.status === "ready").length;
  const chunkCount = docs.reduce((sum, d) => sum + d.chunk_count, 0);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-52" />
        <Skeleton className="h-44 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Knowledge base</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {docs.length} document{docs.length === 1 ? "" : "s"} · {readyCount} ready · {chunkCount} chunks
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={() => setUrlOpen(true)}>
            <Globe className="h-4 w-4" /> Ingest URL
          </Button>
          <Button variant="outline" size="sm" onClick={() => setTextOpen(true)}>
            <NotebookPen className="h-4 w-4" /> Add text
          </Button>
          <Button variant="secondary" size="sm" onClick={() => setFaqOpen(true)}>
            <Plus className="h-4 w-4" /> Add FAQ
          </Button>
        </div>
      </div>

      <UploadZone onFile={uploadFile} busy={uploading} />
      {uploading && (
        <div className="flex items-center gap-3">
          <Progress value={progress} />
          <span className="text-xs text-muted-foreground">Chunking & embedding…</span>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-4 w-4 text-primary" /> Search knowledge
            </CardTitle>
            <CardDescription>Ask a question — the RAG pipeline finds the most relevant chunks.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-2">
              <Input
                placeholder="e.g. how do I reset my password?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && search()}
              />
              <Button onClick={search} disabled={searching || !query.trim()}>
                {searching ? <Spinner /> : <Search className="h-4 w-4" />}
                Search
              </Button>
            </div>

            {results === null && (
              <p className="rounded-md bg-muted/50 p-3 text-xs text-muted-foreground">
                Hits are scored by semantic relevance. Sources come only from <b>this</b> workspace —
                tenants can never see each other&apos;s knowledge.
              </p>
            )}
            {results !== null && results.length === 0 && (
              <p className="rounded-md bg-muted/50 p-3 text-xs text-muted-foreground">
                No matches. Add more documents or try different wording.
              </p>
            )}
            {results?.map((hit) => (
              <div key={hit.id} className="rounded-lg border border-border p-3">
                <div className="mb-1 flex items-center justify-between gap-2">
                  <span className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
                    <FileText className="h-3.5 w-3.5" /> {hit.filename}
                  </span>
                  <span className="rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-semibold text-primary">
                    {Math.round(hit.score * 100)}%
                  </span>
                </div>
                <p className="line-clamp-3 text-sm text-foreground">{hit.text}</p>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-primary" /> Tags
            </CardTitle>
            <CardDescription>Organize documents by topic.</CardDescription>
          </CardHeader>
          <CardContent>
            {tags.length === 0 ? (
              <p className="text-sm text-muted-foreground">No tags yet — they appear as you add documents.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <Badge key={tag.name} variant="secondary" className="px-3 py-1">
                    {tag.name} <span className="ml-1 text-muted-foreground">· {tag.count}</span>
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Documents</CardTitle>
          <CardDescription>Everything your AI crew can ground its answers on.</CardDescription>
        </CardHeader>
        <CardContent>
          {docs.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-10 text-center">
              <BookOpen className="h-10 w-10 text-muted-foreground/40" />
              <p className="text-sm font-medium">Your knowledge base is empty</p>
              <p className="max-w-sm text-xs text-muted-foreground">
                Upload a PDF, DOCX or Markdown file — or add an FAQ — and your AI crew can start answering
                from it immediately.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-border text-xs uppercase tracking-wider text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">Document</th>
                    <th className="pb-2 pr-4 font-medium">Source</th>
                    <th className="pb-2 pr-4 font-medium">Status</th>
                    <th className="pb-2 pr-4 font-medium">Chunks</th>
                    <th className="pb-2 pr-4 font-medium">Size</th>
                    <th className="pb-2 pr-4 font-medium">Uploaded</th>
                    <th className="pb-2 text-right font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {docs.map((doc) => {
                    const source = SOURCE_LABELS[doc.source_type] ?? SOURCE_LABELS.upload;
                    return (
                      <tr key={doc.id} className="border-b border-border/60 last:border-0">
                        <td className="py-3 pr-4">
                          <p className="flex items-center gap-2 font-medium">
                            <source.icon className="h-4 w-4 shrink-0 text-muted-foreground" />
                            <span className="truncate">{doc.filename}</span>
                          </p>
                          {doc.tags.length > 0 && (
                            <div className="mt-1 flex flex-wrap gap-1">
                              {doc.tags.map((tag) => (
                                <span
                                  key={tag}
                                  className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground"
                                >
                                  #{tag}
                                </span>
                              ))}
                            </div>
                          )}
                          {doc.error && <p className="mt-1 text-xs text-destructive">{doc.error}</p>}
                        </td>
                        <td className="py-3 pr-4">
                          <Badge variant="secondary">{source.label}</Badge>
                        </td>
                        <td className="py-3 pr-4">
                          <StatusBadge status={doc.status} />
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground">{doc.chunk_count}</td>
                        <td className="py-3 pr-4 text-muted-foreground">{formatBytes(doc.size_bytes)}</td>
                        <td className="py-3 pr-4 text-muted-foreground">{timeAgo(doc.created_at)}</td>
                        <td className="py-3 text-right">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => deleteDoc(doc)}
                            title="Delete document"
                          >
                            <Trash2 className="h-4 w-4 text-muted-foreground hover:text-destructive" />
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Modal open={urlOpen} onClose={() => setUrlOpen(false)} title="Ingest a website" description="Fetch and index the readable text of a public URL.">
        <div className="space-y-3">
          <Label htmlFor="kb-url">Page URL</Label>
          <Input
            id="kb-url"
            placeholder="https://docs.example.com/getting-started"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <div className="flex justify-end gap-2 pt-1">
            <Button variant="ghost" onClick={() => setUrlOpen(false)}>Cancel</Button>
            <Button onClick={submitUrl} disabled={!url.trim()}>
              <Link2 className="h-4 w-4" /> Ingest
            </Button>
          </div>
        </div>
      </Modal>

      <Modal open={textOpen} onClose={() => setTextOpen(false)} title="Add raw text" description="Paste any text (docs, guides, policies) — it is chunked and embedded immediately.">
        <div className="space-y-3">
          <Label htmlFor="text-name">Name</Label>
          <Input
            id="text-name"
            placeholder="e.g. Security policy"
            value={textName}
            onChange={(e) => setTextName(e.target.value)}
          />
          <Label htmlFor="text-content">Content</Label>
          <Textarea
            id="text-content"
            rows={8}
            placeholder="Paste or type the knowledge text…"
            value={textContent}
            onChange={(e) => setTextContent(e.target.value)}
          />
          <div className="flex justify-end gap-2 pt-1">
            <Button variant="ghost" onClick={() => setTextOpen(false)}>Cancel</Button>
            <Button onClick={submitText} disabled={!textName.trim() || !textContent.trim()}>
              <NotebookPen className="h-4 w-4" /> Add text
            </Button>
          </div>
        </div>
      </Modal>

      <Modal open={faqOpen} onClose={() => setFaqOpen(false)} title="Add an FAQ" description="Paste Q&A content — it becomes instantly searchable.">
        <div className="space-y-3">
          <Label htmlFor="faq-name">Name</Label>
          <Input
            id="faq-name"
            placeholder="e.g. Billing FAQ"
            value={faqName}
            onChange={(e) => setFaqName(e.target.value)}
          />
          <Label htmlFor="faq-content">Content</Label>
          <Textarea
            id="faq-content"
            rows={8}
            placeholder={"Q: How do I refund an order?\nA: Go to Settings → Billing and request a refund."}
            value={faqContent}
            onChange={(e) => setFaqContent(e.target.value)}
          />
          <div className="flex justify-end gap-2 pt-1">
            <Button variant="ghost" onClick={() => setFaqOpen(false)}>Cancel</Button>
            <Button onClick={submitFaq} disabled={!faqName.trim() || !faqContent.trim()}>
              <Plus className="h-4 w-4" /> Add FAQ
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
