"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Save } from "lucide-react";

import { apiFetch, type Workspace } from "@/lib/api";
import { useSession } from "@/lib/session";
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
import { WidgetSettings } from "@/components/dashboard/widget-settings";
import { WebhookSettings } from "@/components/dashboard/webhook-settings";

export default function SettingsPage() {
  const { activeWorkspace, refresh, logout } = useSession();
  const { toast } = useToast();
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const isOwner = activeWorkspace?.your_role === "owner";
  const canManage = isOwner || activeWorkspace?.your_role === "admin";

  useEffect(() => {
    if (!activeWorkspace) return;
    apiFetch<Workspace>(`/api/v1/workspaces/${activeWorkspace.slug}`).then((ws) => {
      setWorkspace(ws);
      setName(ws.name);
      setDescription(ws.description ?? "");
    });
  }, [activeWorkspace]);

  const save = async () => {
    if (!activeWorkspace || !name.trim()) return;
    setSaving(true);
    try {
      await apiFetch(`/api/v1/workspaces/${activeWorkspace.slug}`, {
        method: "PATCH",
        body: JSON.stringify({ name: name.trim(), description }),
      });
      toast({ title: "Workspace updated", variant: "success" });
      await refresh();
    } catch (error) {
      toast({
        title: "Could not update workspace",
        description: error instanceof Error ? error.message : "Something went wrong",
        variant: "error",
      });
    } finally {
      setSaving(false);
    }
  };

  const remove = async () => {
    if (!activeWorkspace) return;
    setDeleting(true);
    try {
      await apiFetch(`/api/v1/workspaces/${activeWorkspace.slug}`, { method: "DELETE" });
      toast({ title: "Workspace deleted", variant: "success" });
      window.localStorage.removeItem("td_active_ws");
      await refresh();
      logout();
    } catch (error) {
      toast({
        title: "Could not delete workspace",
        description: error instanceof Error ? error.message : "Something went wrong",
        variant: "error",
      });
      setDeleting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Workspace profile and management.
        </p>
      </div>

      {!workspace ? (
        <Card>
          <CardContent className="space-y-3 p-5">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
          </CardContent>
        </Card>
      ) : (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Workspace profile</CardTitle>
              <CardDescription>This information is visible to all members.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="ws-name">Name</Label>
                <Input
                  id="ws-name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={!canManage}
                />
              </div>
              <div>
                <Label htmlFor="ws-desc">Description</Label>
                <textarea
                  id="ws-desc"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  disabled={!canManage}
                  rows={3}
                  className="flex w-full rounded-md border border-input bg-card px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
                  placeholder="What does your team support?"
                />
              </div>
              <div>
                <Label>Address</Label>
                <Input value={`/${workspace.slug}`} disabled />
                <p className="mt-1 text-xs text-muted-foreground">
                  Used in API routes and URLs. Cannot be changed after creation.
                </p>
              </div>
              {canManage && (
                <div className="flex justify-end pt-2">
                  <Button onClick={save} disabled={saving || !name.trim()}>
                    {saving ? <Spinner /> : <Save className="h-4 w-4" />}
                    Save changes
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {canManage && <WidgetSettings />}

          {canManage && <WebhookSettings />}

          <Card className="border-destructive/40">
            <CardHeader>
              <CardTitle className="text-destructive">Danger zone</CardTitle>
              <CardDescription>
                Deleting is permanent. All members lose access immediately.
              </CardDescription>
            </CardHeader>
            <CardContent className="flex items-center justify-between gap-3">
              <p className="text-sm text-muted-foreground">
                Permanently delete {workspace.name} and all its data.
              </p>
              {!confirmDelete ? (
                <Button variant="destructive" onClick={() => setConfirmDelete(true)} disabled={!isOwner}>
                  Delete workspace
                </Button>
              ) : (
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-destructive" />
                  <Button variant="ghost" onClick={() => setConfirmDelete(false)}>
                    Cancel
                  </Button>
                  <Button variant="destructive" onClick={remove} disabled={deleting}>
                    {deleting && <Spinner />}
                    Confirm delete
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
