"use client";

import { useEffect, useState } from "react";
import { MessageSquare } from "lucide-react";

import { apiFetch, type WidgetConfig } from "@/lib/api";
import { SessionProvider, useSession } from "@/lib/session";

function WidgetDemo() {
  const { activeWorkspace } = useSession();
  const [snippet, setSnippet] = useState("");
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    if (!activeWorkspace) return;
    apiFetch<WidgetConfig>(`/api/v1/workspaces/${activeWorkspace.slug}/widget/config`)
      .then((cfg) => {
        setEnabled(cfg.widget_enabled);
        if (cfg.widget_token) {
          setSnippet(
            `<script src="http://localhost:3000/widget.js" data-widget-src="${cfg.widget_url}" data-base="http://localhost:8000" data-token="${cfg.widget_token}" data-brand="${activeWorkspace.name}"></script>`,
          );
        }
      })
      .catch(() => {});
  }, [activeWorkspace]);

  useEffect(() => {
    if (!snippet) return;
    const existing = document.querySelector("script[data-widget-src]");
    if (existing) existing.remove();
    const s = document.createElement("script");
    s.setAttribute("data-widget-src", extract(snippet, "data-widget-src"));
    s.setAttribute("data-base", extract(snippet, "data-base"));
    s.setAttribute("data-token", extract(snippet, "data-token"));
    s.setAttribute("data-brand", activeWorkspace?.name ?? "Support Assistant");
    s.src = "/widget.js";
    document.body.appendChild(s);
  }, [snippet, activeWorkspace]);

  return (
    <div className="mx-auto max-w-3xl space-y-6 p-8">
      <div className="flex items-center gap-2">
        <MessageSquare className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-semibold tracking-tight">Widget preview</h1>
      </div>
      <p className="text-sm text-muted-foreground">
        {activeWorkspace ? (
          <>
            Live preview for <b>{activeWorkspace.name}</b>. The floating bubble in the corner is
            your embedded AI widget.{" "}
            {enabled ? (
              <span className="text-success">Enabled.</span>
            ) : (
              <span className="text-warning">
                The widget is disabled — enable it in Settings → Public widget.
              </span>
            )}
          </>
        ) : (
          "Log in to preview your workspace widget."
        )}
      </p>
      <pre className="rounded-md bg-muted/50 p-4 text-[11px] leading-relaxed text-muted-foreground">
        {snippet || "Enable the widget in Settings to generate your embed snippet."}
      </pre>
    </div>
  );
}

function extract(snippet: string, attr: string): string {
  const m = snippet.match(new RegExp(`${attr}="([^"]*)"`));
  return m ? m[1] : "";
}

export default function WidgetDemoPage() {
  return (
    <SessionProvider>
      <WidgetDemo />
    </SessionProvider>
  );
}
