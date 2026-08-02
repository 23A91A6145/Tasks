"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { SessionProvider, useSession } from "@/lib/session";
import { AppShell } from "@/components/shell";
import { FullScreenLoader } from "@/components/ui/spinner";

function AdminGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user && !user.is_super_admin) {
      router.replace("/app/dashboard");
    }
  }, [loading, user, router]);

  if (loading || !user) return <FullScreenLoader />;
  if (!user.is_super_admin) return <FullScreenLoader />;

  return <>{children}</>;
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <AppShell>
        <AdminGuard>{children}</AdminGuard>
      </AppShell>
    </SessionProvider>
  );
}
