"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, MailCheck } from "lucide-react";

import { ApiError, requestPasswordReset } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<{ message: string; resetLink?: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await requestPasswordReset(email);
      setDone({ message: result.message, resetLink: result.reset_link });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Reset your password</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Enter the email you signed up with and we&apos;ll send you a reset link.
        </p>
      </div>

      {done ? (
        <div className="space-y-4">
          <div className="flex items-start gap-3 rounded-md border border-emerald-500/30 bg-emerald-500/10 px-3 py-3 text-sm text-emerald-700">
            <MailCheck className="mt-0.5 h-4 w-4 shrink-0" />
            <div className="space-y-2">
              <p>{done.message}</p>
              {done.resetLink && (
                <div>
                  <p className="mb-1 text-xs font-medium">Dev mode reset link (click to continue):</p>
                  <a
                    href={done.resetLink}
                    className="break-all text-xs text-emerald-700 underline"
                  >
                    {done.resetLink}
                  </a>
                </div>
              )}
            </div>
          </div>
          <Button variant="outline" className="w-full" onClick={() => setDone(null)}>
            Try a different email
          </Button>
        </div>
      ) : (
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
          <Button type="submit" className="w-full" size="lg" disabled={loading || !email}>
            {loading && <Spinner />}
            Send reset link
          </Button>
        </form>
      )}

      <p className="text-center text-sm text-muted-foreground">
        Remembered it?{" "}
        <Link href="/login" className="font-medium text-primary hover:underline">
          Back to sign in
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
