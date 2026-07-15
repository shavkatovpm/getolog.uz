"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut, type LucideIcon } from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
}

interface Props {
  navItems: NavItem[];
  eyebrow: string;
  onSignOut: () => void;
  headerExtra?: React.ReactNode;
  children: React.ReactNode;
}

/** Desktop'da chap sidebar, mobile'da pastki tab-panel bo'lgan umumiy dashboard qobig'i. */
export function DashboardShell({ navItems, eyebrow, onSignOut, headerExtra, children }: Props) {
  const pathname = usePathname();

  function isActive(href: string) {
    return href === pathname || (href !== "/admin" && href !== "/owner" && pathname.startsWith(href));
  }

  return (
    <div className="min-h-screen bg-h-bg lg:flex">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:w-60 lg:flex-shrink-0 lg:flex-col lg:border-r lg:border-h-border lg:bg-h-surface">
        <div className="px-5 py-5">
          <div className="text-xs font-medium tracking-wide text-h-muted uppercase">{eyebrow}</div>
          <div className="text-base font-medium text-h-ink">GETOLOG</div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition-colors ${
                  active
                    ? "bg-h-accent/10 font-medium text-h-accent"
                    : "text-h-muted hover:bg-h-bg hover:text-h-ink"
                }`}
              >
                <Icon size={17} strokeWidth={2} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-h-border p-3">
          <button
            onClick={onSignOut}
            className="flex w-full items-center gap-2.5 rounded-md px-3 py-2 text-sm text-h-muted transition-colors hover:bg-h-bg hover:text-h-ink"
          >
            <LogOut size={17} strokeWidth={2} />
            Chiqish
          </button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        {/* Mobile top bar */}
        <header className="flex items-center justify-between border-b border-h-border bg-h-surface px-4 py-3 lg:hidden">
          <div>
            <div className="text-[11px] font-medium tracking-wide text-h-muted uppercase">{eyebrow}</div>
            <div className="text-sm font-medium text-h-ink">GETOLOG</div>
          </div>
          {headerExtra}
        </header>

        {/* Desktop top bar (kanal tanlash kabi qo'shimcha nazoratlar uchun) */}
        {headerExtra && (
          <header className="hidden border-b border-h-border bg-h-surface px-8 py-3 lg:block">
            {headerExtra}
          </header>
        )}

        <main className="flex-1 px-4 py-6 pb-24 lg:px-8 lg:py-8 lg:pb-8">{children}</main>

        {/* Mobile bottom nav */}
        <nav className="fixed inset-x-0 bottom-0 z-10 flex border-t border-h-border bg-h-surface lg:hidden">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex flex-1 flex-col items-center gap-1 py-2.5 text-[11px] ${
                  active ? "text-h-accent" : "text-h-muted"
                }`}
              >
                <Icon size={19} strokeWidth={2} />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
