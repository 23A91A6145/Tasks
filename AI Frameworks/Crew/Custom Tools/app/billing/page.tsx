"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, CreditCard, ShieldCheck, Sparkles, Zap } from "lucide-react";

import { apiFetch, type BillingSummary, type UsageItem } from "@/lib/api";
import { useSession } from "@/lib/session";
import { formatDate } from "@/lib/utils";
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
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/toast";

function usageValue(item: UsageItem): string {
  if (item.remaining === "unlimited") return "Unlimited";
  return `${item.used.toLocaleString()} / ${item.limit.toLocaleString()} ${item.unit}`;
}

function UsageMeter({ item }: { item: UsageItem }) {
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between gap-2">
        <p className="text-sm font-medium">{item.label}</p>
        <p className="text-xs text-muted-foreground">
          {item.remaining === "unlimited"
            ? "unlimited"
            : `${item.remaining} ${item.unit} left`}
        </p>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted">
        <div
          className={`h-full rounded-full transition-all ${
            item.percent >= 90
              ? "bg-destructive"
              : item.percent >= 70
                ? "bg-warning"
                : "bg-primary"
          }`}
          style={{ width: `${Math.max(item.percent, item.used > 0 ? 3 : 0)}%` }}
        />
      </div>
      <p className="mt-1 text-xs text-muted-foreground">{usageValue(item)}</p>
    </div>
  );
}

export default function BillingPage() {
  const { activeWorkspace } = useSession();
  const { toast } = useToast();
  const [summary, setSummary] = useState<BillingSummary | null>(null);
  const [switching, setSwitching] = useState<string | null>(null);

  const slug = activeWorkspace?.slug;
  const isOwner = activeWorkspace?.your_role === "owner";

  const load = useCallback(async () => {
    if (!slug) return;
    const result = await apiFetch<BillingSummary>(`/api/v1/workspaces/${slug}/billing/summary`);
    setSummary(result);
  }, [slug]);

  useEffect(() => {
    if (!slug) return;
    load().catch(() => toast({ title: "Could not load billing", variant: "error" }));
  }, [slug, load, toast]);

  const changePlan = async (plan: string) => {
    if (!slug) return;
    setSwitching(plan);
    try {
      const result = await apiFetch<BillingSummary>(`/api/v1/workspaces/${slug}/billing/change`, {
        method: "POST",
        body: JSON.stringify({ plan }),
      });
      setSummary(result);
      toast({ title: `Switched to ${plan}`, variant: "success" });
    } catch (error) {
      toast({
        title: "Could not change plan",
        description: error instanceof Error ? error.message : undefined,
        variant: "error",
      });
    } finally {
      setSwitching(null);
    }
  };

  if (!summary) {
    return (
      <div className="space-y-5">
        <Skeleton className="h-8 w-56" />
        <Skeleton className="h-44 w-full" />
        <div className="grid gap-4 md:grid-cols-3">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight">
          <CreditCard className="h-5 w-5 text-primary" /> Billing &amp; plans
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Your billing cycle runs {formatDate(summary.period_start)} →{" "}
          {formatDate(summary.period_end)}. Limits are enforced automatically.
        </p>
      </div>

      <Card className="overflow-hidden">
        <div className="bg-gradient-to-r from-indigo-500 to-violet-600 p-6 text-white">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm text-white/80">Current plan</p>
              <p className="text-3xl font-bold capitalize">{summary.plan}</p>
            </div>
            <Badge className="border border-white/30 bg-white/15 text-white">
              <Zap className="h-3.5 w-3.5" /> Active
            </Badge>
          </div>
        </div>
        <CardContent className="space-y-5 p-6">
          {summary.items.map((item) => (
            <UsageMeter key={item.key} item={item} />
          ))}
        </CardContent>
      </Card>

      <div>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Available plans
        </h2>
        <div className="grid gap-4 md:grid-cols-3">
          {summary.all_plans.map((plan) => {
            const current = plan.key === summary.plan;
            return (
              <Card
                key={plan.key}
                className={`flex flex-col ${current ? "border-primary shadow-md" : ""}`}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="capitalize">{plan.name}</CardTitle>
                    {current && <Badge>Current</Badge>}
                  </div>
                  <div className="mt-2 flex items-baseline gap-1">
                    <span className="text-3xl font-bold">
                      {plan.price_month === 0 ? "$0" : `$${plan.price_month}`}
                    </span>
                    <span className="text-sm text-muted-foreground">/month</span>
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-1">
                  <ul className="space-y-2.5 text-sm">
                    <li className="flex items-start gap-2">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                      <span className="text-muted-foreground">
                        {plan.requests_per_month === 0
                          ? "Unlimited AI requests"
                          : `${plan.requests_per_month.toLocaleString()} AI requests / month`}
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                      <span className="text-muted-foreground">
                        {plan.knowledge_docs === 0
                          ? "Unlimited knowledge documents"
                          : `${plan.knowledge_docs} knowledge documents`}
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                      <span className="text-muted-foreground">
                        {plan.seats === 0 ? "Unlimited team seats" : `${plan.seats} team seats`}
                      </span>
                    </li>
                    <li className="flex items-start gap-2">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                      <span className="text-muted-foreground">
                        {plan.advanced_analytics
                          ? "Advanced analytics included"
                          : "Core analytics"}
                      </span>
                    </li>
                  </ul>
                </CardContent>
                <CardContent className="pt-0">
                  <Button
                    className="w-full"
                    variant={current ? "outline" : "default"}
                    disabled={current || switching !== null}
                    onClick={() => changePlan(plan.key)}
                  >
                    {switching === plan.key ? (
                      <Spinner />
                    ) : current ? (
                      <ShieldCheck className="h-4 w-4" />
                    ) : (
                      <Sparkles className="h-4 w-4" />
                    )}
                    {current ? "Current plan" : `Switch to ${plan.name}`}
                  </Button>
                  {!isOwner && !current && (
                    <p className="mt-1.5 text-center text-xs text-muted-foreground">
                      Only the workspace owner can change the plan.
                    </p>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
