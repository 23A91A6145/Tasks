"use client";

import { useCallback, useEffect, useState } from "react";
import { Activity, Building2, Crown, ShieldCheck, Users } from "lucide-react";

import { apiFetch, type AdminOverview } from "@/lib/api";
import { KpiCard, KpiSkeleton } from "@/components/dashboard/kpi-card";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export default function AdminPage() {
  const [data, setData] = useState<AdminOverview | null>(null);

  const load = useCallback(async () => {
    setData(await apiFetch<AdminOverview>("/api/v1/admin/overview"));
  }, []);

  useEffect(() => {
    load().catch(() => {});
  }, [load]);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl font-semibold tracking-tight">Platform Admin</h1>
          <Badge variant="default">Super admin</Badge>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          TenantDesk-wide overview — all workspaces, users and activity across the platform.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {data ? (
          <>
            <KpiCard title="Users" value={data.users} icon={Users} accent="primary" />
            <KpiCard title="Workspaces" value={data.workspaces} icon={Building2} accent="success" />
            <KpiCard title="Memberships" value={data.memberships} icon={Crown} accent="warning" />
            <KpiCard title="Activities" value={data.activities} icon={Activity} accent="primary" />
          </>
        ) : (
          <>
            <KpiSkeleton />
            <KpiSkeleton />
            <KpiSkeleton />
            <KpiSkeleton />
          </>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            Plan catalog
          </CardTitle>
          <CardDescription>Limits enforced per workspace on each subscription plan.</CardDescription>
        </CardHeader>
        <CardContent>
          {data ? (
            <div className="grid gap-3 sm:grid-cols-3">
              {Object.entries(data.plans).map(([key, plan]) => (
                <div key={key} className="rounded-lg border p-4">
                  <p className="text-sm font-medium capitalize">
                    {key} <span className="ml-1 text-xs text-muted-foreground">plan</span>
                  </p>
                  <dl className="mt-3 space-y-1 text-sm">
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Requests / mo</dt>
                      <dd>{plan.requests_per_month}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Knowledge docs</dt>
                      <dd>{plan.knowledge_docs}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-muted-foreground">Seats</dt>
                      <dd>{plan.seats}</dd>
                    </div>
                  </dl>
                </div>
              ))}
            </div>
          ) : (
            <Skeleton className="h-28 w-full" />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
