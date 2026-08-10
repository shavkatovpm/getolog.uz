"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Home, CreditCard, Users, Settings, WalletCards } from "lucide-react";
import { clearAuth, getAuth } from "@/lib/api";
import { ChannelProvider, useChannels } from "@/lib/channel-context";
import { MeProvider, useMe } from "@/lib/me-context";
import { computeTariffUsage } from "@/lib/tariff";
import { DashboardShell, NavItem } from "@/components/DashboardShell";
import { TariffBadge } from "@/components/TariffBadge";
import { Select } from "@/components/Select";

const NAV_ITEMS: NavItem[] = [
  { href: "/admin", label: "Bosh sahifa", icon: Home },
  { href: "/admin/subscribers", label: "Obunachilar", icon: Users },
  { href: "/admin/payments", label: "To'lovlar holati", icon: CreditCard },
  { href: "/admin/plans", label: "To'lov sozlamalari", icon: WalletCards },
  { href: "/admin/settings", label: "Sozlamalar", icon: Settings },
];

function ChannelSwitcher() {
  const { channels, selectedChannelId, setSelectedChannelId, loading } = useChannels();
  if (loading || channels.length === 0) return null;

  if (channels.length === 1) {
    const only = channels[0];
    return (
      <span className="text-sm font-medium text-h-ink">
        {only.title}
        {only.chat_type === "group" && <span className="ml-1.5 text-xs text-h-muted">(guruh)</span>}
      </span>
    );
  }

  return (
    <Select
      value={selectedChannelId ?? ""}
      onChange={(e) => setSelectedChannelId(Number(e.target.value))}
      className="py-1.5 pl-2 text-sm"
    >
      {channels.map((c) => (
        <option key={c.id} value={c.id}>
          {c.title}
          {c.chat_type === "group" ? " (guruh)" : ""}
        </option>
      ))}
    </Select>
  );
}

function AdminShellInner({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { channels, loading, error } = useChannels();
  const { me } = useMe();

  const usage = me
    ? computeTariffUsage({
        tariffStartedAt: me.tariff_started_at,
        tariffExpiry: me.tariff_expiry,
        subscriberCount: me.subscriber_count,
        subscriberLimit: me.subscriber_limit,
      })
    : null;

  function signOut() {
    clearAuth();
    router.replace("/");
  }

  return (
    <DashboardShell
      navItems={NAV_ITEMS}
      mobileNavOrder={["/admin/plans", "/admin/payments", "/admin/subscribers", "/admin/settings"]}
      eyebrow="Admin"
      onSignOut={signOut}
      usagePercent={usage?.percent}
      usageTone={usage?.tone}
      headerExtra={<ChannelSwitcher />}
      headerEnd={<TariffBadge />}
    >
      {error ? (
        <p className="rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      ) : !loading && channels.length === 0 ? (
        <div className="mx-auto max-w-md py-12 text-center">
          <h2 className="mb-2 text-base font-medium text-h-ink">Hali kanal ulanmagan</h2>
          <p className="text-sm text-h-muted">
            Avval GETOLOG bosh botiga /start yuborib, botingizni kanalga admin qilib ulang.
          </p>
        </div>
      ) : (
        // `loading` hali true bo'lsa ham shu yerda `children` render qilinadi —
        // sahifaning o'zi (masalan Obunachilar) `useChannels().loading`ni o'z
        // ma'lumotlari bilan birlashtirib, YAGONA uzluksiz loader ko'rsatadi.
        // Bu yerda alohida loader chiqarilsa, ikkita ketma-ket loader (avval
        // shu yerdagi, keyin sahifaning o'zinikidan) paydo bo'lardi — chunki
        // ikkalasi alohida LogoLoader nusxasi bo'lib, chizish animatsiyasi
        // qayta boshidan ishga tushib qolardi.
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
      <MeProvider>
        <AdminShellInner>{children}</AdminShellInner>
      </MeProvider>
    </ChannelProvider>
  );
}
