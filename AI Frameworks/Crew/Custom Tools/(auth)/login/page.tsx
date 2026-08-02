"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Sparkles } from "lucide-react";

import { apiFetch, ApiError, setTokens, type AuthResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [demoing, setDemoing] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<AuthResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
        auth: false,
      });
      setTokens(data.access_token, data.refresh_token);
      router.push("/app/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const tryDemo = async () => {
    setDemoing(true);
    setError(null);
    try {
      const data = await apiFetch<AuthResponse>("/api/v1/auth/demo", {
        method: "POST",
        auth: false,
      });
      setTokens(data.access_token, data.refresh_token);
      router.push("/app/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Could not open the demo");
    } finally {
      setDemoing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Welcome back</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Sign in to your workspace — or jump straight into the live demo.
        </p>
      </div>

      <Button
        type="button"
        variant="outline"
        className="w-full"
        size="lg"
        onClick={tryDemo}
        disabled={demoing}
      >
        {demoing ? <Spinner /> : <Sparkles className="h-4 w-4" />}
        {demoing ? "Opening demo…" : "Try the live demo — no account needed"}
      </Button>

      <div className="flex items-center gap-3">
        <span className="h-px flex-1 bg-border" />
        <span className="text-xs uppercase tracking-wider text-muted-foreground">or sign in</span>
        <span className="h-px flex-1 bg-border" />
      </div>

      <form onSubmit={submit} className="space-y-4">
        {error && (
          <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2.5 text-sm text-destructive">
            {error}
          </div>
        )}
        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
          />
        </div>
        <div className="flex items-center justify-between">
          <Label htmlFor="password">Password</Label>
          <Link
            href="/forgot-password"
            className="text-xs font-medium text-primary hover:underline"
          >
            Forgot password?
          </Link>
        </div>
        <Input
          id="password"
          type="password"
          autoComplete="current-password"
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <Button type="submit" className="w-full" size="lg" disabled={loading || !email || !password}>
          {loading && <Spinner />}
          Sign in
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        No account yet?{" "}
        <Link href="/register" className="font-medium text-primary hover:underline">
          Create one free
        </Link>
      </p>

      <div className="text-center">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          Back to home
        </Link>
      </div>
    </div>
  );
}
