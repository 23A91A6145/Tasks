"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";

import { apiFetch, ApiError, setTokens, type AuthResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [workspaceName, setWorkspaceName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch<AuthResponse>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({
          full_name: fullName,
          email,
          password,
          workspace_name: workspaceName.trim() || undefined,
        }),
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Create your account</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Free forever during development. Add a workspace name to get started instantly.
        </p>
      </div>

      <form onSubmit={submit} className="space-y-4">
        {error && (
          <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2.5 text-sm text-destructive">
            {error}
          </div>
        )}
        <div>
          <Label htmlFor="full-name">Full name</Label>
          <Input
            id="full-name"
            autoComplete="name"
            placeholder="Ada Lovelace"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            autoFocus
          />
        </div>
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
          />
        </div>
        <div>
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete="new-password"
            placeholder="8+ characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
        </div>
        <div>
          <Label htmlFor="workspace">Workspace name (optional)</Label>
          <Input
            id="workspace"
            placeholder="Acme Support"
            value={workspaceName}
            onChange={(e) => setWorkspaceName(e.target.value)}
          />
          <p className="mt-1 text-xs text-muted-foreground">
            Skip this and you&apos;ll create one right after signing up.
          </p>
        </div>
        <Button
          type="submit"
          className="w-full"
          size="lg"
          disabled={loading || !fullName || !email || password.length < 8}
        >
          {loading && <Spinner />}
          Create account
        </Button>
      </form>

      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-primary hover:underline">
          Sign in
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
