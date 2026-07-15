"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CreditCard, LayoutDashboard, Radio, Users } from "lucide-react";
import { clearAuth, getAuth } from "@/lib/api";
import { DashboardShell, NavItem } from "@/components/DashboardShell";

const NAV_ITEMS: NavItem[] = [
  { href: "/owner", label: "Statistika", icon: LayoutDashboard },
  { href: "/owner/admins", label: "Adminlar", icon: Users },
  { href: "/owner/channels", label: "Kanallar", icon: Radio },
  { href: "/owner/payments", label: "To'lovlar", icon: CreditCard },
];

export default function OwnerLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [authorized] = useState(() => {
    const auth = getAuth();
    return !!auth && auth.role === "owner";
  });

  useEffect(() => {
    if (!authorized) router.replace("/");
  }, [authorized, router]);

  if (!authorized) return null;

  function signOut() {
    clearAuth();
    router.replace("/");
  }

  return (
    <DashboardShell navItems={NAV_ITEMS} eyebrow="Owner" onSignOut={signOut}>
      {children}
    </DashboardShell>
  );
}
