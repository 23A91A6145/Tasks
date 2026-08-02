"use client";

import { useCallback, useEffect, useState } from "react";
import { Building2 } from "lucide-react";

import { apiFetch, type AdminWorkspace } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminWorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<AdminWorkspace[] | null>(null);

  const load = useCallback(async () => {
    setWorkspaces(await apiFetch<AdminWorkspace[]>("/api/v1/admin/workspaces"));
  }, []);

  useEffect(() => {
    load().catch(() => {});
  }, [load]);

  const planColor: Record<string, string> = {
    free: "bg-muted text-muted-foreground",
    pro: "bg-primary/10 text-primary",
    enterprise: "bg-warning/10 text-warning",
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Workspaces</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Every tenant organization on the platform and its current plan.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-primary" />
            All tenants
          </CardTitle>
          <CardDescription>{workspaces ? `${workspaces.length} workspace(s)` : "Loading…"}</CardDescription>
        </CardHeader>
        <CardContent>
          {!workspaces ? (
            <Skeleton className="h-32 w-full" />
          ) : workspaces.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">No workspaces yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs uppercase tracking-wider text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">Name</th>
                    <th className="pb-2 pr-4 font-medium">Slug</th>
                    <th className="pb-2 pr-4 font-medium">Plan</th>
                    <th className="pb-2 pr-4 font-medium">Members</th>
                    <th className="pb-2 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {workspaces.map((w) => (
                    <tr key={w.id} className="border-b last:border-0">
                      <td className="py-3 pr-4 font-medium">{w.name}</td>
                      <td className="py-3 pr-4 text-muted-foreground">{w.slug}</td>
                      <td className="py-3 pr-4">
                        <Badge className={planColor[w.plan] ?? ""}>{w.plan}</Badge>
                      </td>
                      <td className="py-3 pr-4">{w.member_count}</td>
                      <td className="py-3 text-muted-foreground">
                        {new Date(w.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
