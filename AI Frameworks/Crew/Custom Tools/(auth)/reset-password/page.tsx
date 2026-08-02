"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowLeft, CheckCircle2 } from "lucide-react";

import { ApiError, resetPassword } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    if (password !== confirm) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }
    try {
      const result = await resetPassword(token, password);
      setDone(result.message);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <div className="space-y-4">
        <div className="flex items-start gap-3 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-3 py-3 text-sm text-emerald-700">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
          <p>{done}</p>
        </div>
        <Link href="/login" className="block">
          <Button className="w-full" size="lg">
            Sign in with your new password
          </Button>
        </Link>
      </div>
    );
  }

  if (!token) {
    return (
      <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2.5 text-sm text-destructive">
        This reset link is missing its token. Please use the link from your email, or request a new
        one.
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      {error && (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2.5 text-sm text-destructive">
          {error}
        </div>
      )}
      <div>
        <Label htmlFor="password">New password</Label>
        <Input
          id="password"
          type="password"
          autoComplete="new-password"
          placeholder="8+ characters"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          autoFocus
        />
      </div>
      <div>
        <Label htmlFor="confirm">Confirm new password</Label>
        <Input
          id="confirm"
          type="password"
          autoComplete="new-password"
          placeholder="Repeat it"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          required
          minLength={8}
        />
      </div>
      <Button
        type="submit"
        className="w-full"
        size="lg"
        disabled={loading || password.length < 8 || !confirm}
      >
        {loading && <Spinner />}
        Update password
      </Button>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Choose a new password</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Your reset link is valid for 15 minutes.
        </p>
      </div>

      <Suspense fallback={<div className="h-40 animate-pulse rounded-lg bg-muted" />}>
        <ResetPasswordForm />
      </Suspense>

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
