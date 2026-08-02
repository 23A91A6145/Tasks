import { Check, Sparkles } from "lucide-react";
import Link from "next/link";

import { Navbar } from "@/components/landing/navbar";
import { Footer } from "@/components/landing/footer";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const PLANS = [
  {
    key: "free",
    name: "Free",
    price: "$0",
    period: "forever",
    description: "For teams trying out AI support.",
    features: ["500 AI requests / month", "10 knowledge documents", "5 team seats", "100 MB storage", "Core analytics", "Community support"],
    highlight: false,
    cta: "Start free",
  },
  {
    key: "pro",
    name: "Pro",
    price: "$49",
    period: "/month",
    description: "For growing support teams.",
    features: ["5,000 AI requests / month", "100 knowledge documents", "50 team seats", "2 GB storage", "Priority processing", "Advanced analytics"],
    highlight: true,
    cta: "Start free trial",
  },
  {
    key: "enterprise",
    name: "Enterprise",
    price: "$299",
    period: "/month",
    description: "For organizations at scale.",
    features: ["Unlimited AI requests", "Unlimited knowledge documents", "Unlimited team seats", "Unlimited storage", "Advanced analytics", "Dedicated support"],
    highlight: false,
    cta: "Contact us",
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <section className="mx-auto max-w-6xl px-4 pb-20 pt-14 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <Badge variant="secondary">
            <Sparkles className="h-3.5 w-3.5" /> Simple pricing
          </Badge>
          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
            Free to start, scales with you
          </h1>
          <p className="mt-4 text-lg text-muted-foreground">
            Every plan includes full tenant isolation, unlimited workspaces and usage metering.
            Switch plans anytime from the billing page — limits are enforced automatically.
          </p>
        </div>

        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {PLANS.map((plan) => (
            <Card
              key={plan.key}
              className={`flex flex-col ${plan.highlight ? "border-primary shadow-lg" : ""}`}
            >
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>{plan.name}</CardTitle>
                  {plan.highlight && <Badge>Most popular</Badge>}
                </div>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-3xl font-bold">{plan.price}</span>
                  <span className="text-sm text-muted-foreground">{plan.period}</span>
                </div>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1">
                <ul className="space-y-2.5">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2 text-sm">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                      <span className="text-muted-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
              <CardFooter>
                <Link href="/register" className="w-full">
                  <Button className="w-full" variant={plan.highlight ? "default" : "outline"}>
                    {plan.cta}
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          ))}
        </div>

        <p className="mt-8 text-center text-xs text-muted-foreground">
          No credit card required to start · all core features work on the free tier.
        </p>
      </section>

      <Footer />
    </div>
  );
}
