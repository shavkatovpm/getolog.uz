"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LayoutDashboard, Tag, CreditCard, Users, Settings } from "lucide-react";
import { clearAuth, getAuth } from "@/lib/api";
import { ChannelProvider, useChannels } from "@/lib/channel-context";
import { DashboardShell, NavItem } from "@/components/DashboardShell";

const NAV_ITEMS: NavItem[] = [
  { href: "/admin", label: "Bosh sahifa", icon: LayoutDashboard },
  { href: "/admin/plans", label: "Tariflar", icon: Tag },
  { href: "/admin/payments", label: "To'lovlar", icon: CreditCard },
  { href: "/admin/subscribers", label: "Obunachilar", icon: Users },
  { href: "/admin/settings", label: "Sozlamalar", icon: Settings },
];

function ChannelSwitcher() {
  const { channels, selectedChannelId, setSelectedChannelId, loading } = useChannels();
  if (loading || channels.length <= 1) return null;
  return (
    <select
      value={selectedChannelId ?? ""}
      onChange={(e) => setSelectedChannelId(Number(e.target.value))}
      className="rounded-md border border-h-border bg-h-surface px-2 py-1.5 text-sm text-h-ink"
    >
      {channels.map((c) => (
        <option key={c.id} value={c.id}>
          {c.title}
        </option>
      ))}
    </select>
  );
}

function AdminShellInner({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { channels, loading, error } = useChannels();

  function signOut() {
    clearAuth();
    router.replace("/");
  }

  return (
    <DashboardShell
      navItems={NAV_ITEMS}
      eyebrow="Admin"
      onSignOut={signOut}
      headerExtra={<ChannelSwitcher />}
    >
      {loading ? (
        <p className="text-sm text-h-muted">Yuklanmoqda...</p>
      ) : error ? (
        <p className="rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      ) : channels.length === 0 ? (
        <div className="mx-auto max-w-md py-12 text-center">
          <h2 className="mb-2 text-base font-medium text-h-ink">Hali kanal ulanmagan</h2>
          <p className="text-sm text-h-muted">
            Avval GETOLOG bosh botiga /start yuborib, botingizni kanalga admin qilib ulang.
          </p>
        </div>
      ) : (
        children
      )}
    </DashboardShell>
  );
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [authorized] = useState(() => {
    const auth = getAuth();
    return !!auth && auth.role === "admin";
  });

  useEffect(() => {
    if (!authorized) router.replace("/");
  }, [authorized, router]);

  if (!authorized) return null;

  return (
    <ChannelProvider>
      <AdminShellInner>{children}</AdminShellInner>
    </ChannelProvider>
  );
}
