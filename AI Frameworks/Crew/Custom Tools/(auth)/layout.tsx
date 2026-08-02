import Link from "next/link";
import { Building2, Bot, BookOpen, ShieldCheck, Zap } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-800 p-12 text-white lg:flex">
        <div className="absolute -right-24 -top-24 h-96 w-96 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute -bottom-32 -left-24 h-96 w-96 rounded-full bg-violet-400/20 blur-3xl" />

        <Link href="/" className="relative flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/15 backdrop-blur">
            <Building2 className="h-5 w-5" />
          </div>
          <span className="text-lg font-semibold tracking-tight">TenantDesk AI</span>
        </Link>

        <div className="relative space-y-6">
          <h1 className="text-4xl font-bold leading-tight tracking-tight">
            Every company gets its own AI support crew.
          </h1>
          <p className="text-lg text-white/80">
            Isolated knowledge, orchestrated agents and full workspace control — built on
            CrewAI, FastAPI and Next.js.
          </p>
          <div className="grid gap-4 pt-2 sm:grid-cols-2">
            {[
              { icon: ShieldCheck, label: "Tenant isolation", text: "Data never crosses workspaces" },
              { icon: Bot, label: "AI crew", text: "Manager-led hierarchical agents" },
              { icon: BookOpen, label: "Own knowledge", text: "Per-workspace RAG namespace" },
              { icon: Zap, label: "Free stack", text: "Open source & free tiers" },
            ].map((item) => (
              <div key={item.label} className="flex items-start gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/15">
                  <item.icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold">{item.label}</p>
                  <p className="text-xs text-white/70">{item.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <p className="relative text-xs text-white/60">
          © {new Date().getFullYear()} TenantDesk AI — capstone project
        </p>
      </div>

      <div className="flex flex-1 flex-col items-center justify-center px-4 py-12">
        <div className="mb-6 flex items-center gap-2 lg:hidden">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
            <Building2 className="h-4 w-4" />
          </div>
          <span className="font-semibold">TenantDesk AI</span>
        </div>
        <div className="w-full max-w-sm">{children}</div>
      </div>
    </div>
  );
}
