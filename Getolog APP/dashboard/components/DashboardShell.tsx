"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut } from "lucide-react";

export type NavIcon = React.ComponentType<{ size?: number; strokeWidth?: number; className?: string }>;
import { LogoMark } from "@/components/LogoMark";
import { ThemeToggle } from "@/components/ThemeToggle";
import { lockAppShellHeight } from "@/lib/viewport";

export interface NavItem {
  href: string;
  label: string;
  icon: NavIcon;
}

interface Props {
  navItems: NavItem[];
  /** Mobil pastki panelda bosh sahifadan boshqa bo'limlarning tartibi shu
   * href ro'yxati bo'yicha belgilanadi (bosh sahifa avtomatik o'rtaga
   * qo'yiladi) — berilmasa, `navItems` tartibidan foydalaniladi. Desktop
   * sidebar tartibiga bu tegmaydi. */
  mobileNavOrder?: string[];
  eyebrow: string;
  onSignOut: () => void;
  headerExtra?: React.ReactNode;
  /** O'ng chetda, tema tugmasi yonida ko'rsatiladi (masalan tarif belgisi). */
  headerEnd?: React.ReactNode;
  /** 0-100: navbar pastki chegarasida chapdan o'ngga to'ladigan tarif/limit ko'rsatkichi. */
  usagePercent?: number;
  usageTone?: "safe" | "warning" | "danger";
  children: React.ReactNode;
}

const USAGE_BAR_COLOR: Record<string, string> = {
  safe: "bg-h-success",
  warning: "bg-h-warning",
  danger: "bg-h-danger",
};

function UsageBorderBar({ percent, tone }: { percent: number; tone: "safe" | "warning" | "danger" }) {
  return (
    <div className="absolute inset-x-0 bottom-0 h-[3px] bg-h-border">
      <div
        className={`h-full transition-[width] duration-500 ease-out ${USAGE_BAR_COLOR[tone]}`}
        style={{ width: `${Math.max(0, Math.min(100, percent))}%` }}
      />
    </div>
  );
}

/** Desktop'da chap sidebar, mobile'da pastki tab-panel bo'lgan umumiy dashboard qobig'i. */
export function DashboardShell({
  navItems,
  mobileNavOrder,
  eyebrow,
  onSignOut,
  headerExtra,
  headerEnd,
  usagePercent,
  usageTone,
  children,
}: Props) {
  const showUsageBar = usagePercent != null && usageTone != null;
  const pathname = usePathname();

  useEffect(() => lockAppShellHeight(), []);

  function isActive(href: string) {
    return href === pathname || (href !== "/admin" && href !== "/owner" && pathname.startsWith(href));
  }

  const currentLabel = navItems.find((item) => isActive(item.href))?.label ?? eyebrow;

  // Mobile pastki panelda birinchi (bosh sahifa) bo'lim markazga chiqariladi —
  // desktop sidebar tartibiga tegmaydi, faqat mobile render tartibi.
  const [homeItem, ...defaultRest] = navItems;
  const restNavItems = mobileNavOrder
    ? (mobileNavOrder.map((href) => navItems.find((item) => item.href === href)).filter(Boolean) as NavItem[])
    : defaultRest;
  const middleIndex = Math.ceil(restNavItems.length / 2);
  const mobileNavItems = [
    ...restNavItems.slice(0, middleIndex),
    homeItem,
    ...restNavItems.slice(middleIndex),
  ];

  return (
    <div className="min-h-dvh bg-h-bg lg:flex">
      {/* Desktop sidebar */}
      <aside className="hidden lg:sticky lg:top-0 lg:flex lg:h-screen lg:w-60 lg:flex-shrink-0 lg:flex-col lg:border-r lg:border-h-border lg:bg-h-surface">
        <div className="flex items-center gap-2.5 px-5 py-5">
          <LogoMark size={32} />
          <div>
            <div className="text-xs font-medium tracking-wide text-h-muted uppercase">{eyebrow}</div>
            <div className="text-base font-medium text-h-ink">GETOLOG</div>
          </div>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition-[color,background-color] duration-150 ${
                  active
                    ? "bg-h-accent/10 font-medium text-h-accent"
                    : "text-h-muted hover:bg-h-bg hover:text-h-ink"
                }`}
              >
                <span className={`inline-flex ${active ? "animate-nav-icon-in" : ""}`}>
                  <Icon size={17} strokeWidth={2} />
                </span>
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

      {/*
        Mobilda bu qobiq `lockAppShellHeight()` orqali "qulflangan" balandlikka
        (`--app-shell-height` — sahifa ochilgandagi haqiqiy balandlik, klaviatura
        kamaytirsa ham o'zgarmaydi) qattiq bog'lanadi va O'ZI SCROLL QILMAYDI
        (`overflow-hidden`) — header va pastki panel oddiy flex-elementlar sifatida
        yuqorida va pastda qoladi, faqat ORADAGI `<main>` o'z ichida scroll qiladi.
        Shu bilan header/panel klaviatura ochilib-yopilganda HECH QACHON
        siljimaydi — klaviatura ularning ostidagi qismni shunchaki qoplab
        qo'yadi (bu — kutilgan, "sakramaydigan" xatti-harakat). Desktopda
        (`lg:`) bu cheklovlar bekor qilinadi, hujjatning o'zi scroll qiladi.
      */}
      <div className="flex h-[var(--app-shell-height,100dvh)] flex-1 flex-col overflow-hidden lg:h-auto lg:overflow-visible">
        {/* Mobile top bar — ikki qatorli: 1) sarlavha + tema, 2) kanal/tarif nazoratlari */}
        <header
          className={`flex-shrink-0 bg-h-surface lg:hidden ${
            showUsageBar ? "relative" : "border-b border-h-border"
          }`}
        >
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-2">
              <LogoMark size={26} />
              <div>
                <div className="text-[11px] font-medium tracking-wide text-h-muted uppercase">{eyebrow}</div>
                <div className="text-sm font-medium text-h-ink">{currentLabel}</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {headerEnd}
              <ThemeToggle />
            </div>
          </div>
          {headerExtra && (
            <div className="flex items-center justify-end gap-2 overflow-x-auto border-t border-h-border px-4 py-2">
              {headerExtra}
            </div>
          )}
          {showUsageBar && <UsageBorderBar percent={usagePercent} tone={usageTone} />}
        </header>

        {/* Desktop top bar (kanal tanlash, tarif holati kabi qo'shimcha nazoratlar uchun) */}
        <header
          className={`sticky top-0 z-20 hidden items-center justify-between bg-h-surface px-8 py-3 lg:flex ${
            showUsageBar ? "relative" : "border-b border-h-border"
          }`}
        >
          <div className="flex items-center gap-3">{headerExtra}</div>
          <div className="flex items-center gap-3">
            {headerEnd}
            <ThemeToggle />
          </div>
          {showUsageBar && <UsageBorderBar percent={usagePercent} tone={usageTone} />}
        </header>

        <main className="flex-1 overflow-y-auto px-4 py-6 lg:overflow-visible lg:px-8 lg:py-8">
          {/* `key={pathname}` — bo'lim almashganda React shu div'ni qaytadan
              yaratadi, shu bilan kirish animatsiyasi har safar qaytadan
              ishga tushadi (bo'lim o'zgarmasa, animatsiya qayta o'ynamaydi). */}
          <div key={pathname} className="animate-section-in">
            {children}
          </div>
        </main>

        {/* Mobile bottom nav — endi oddiy flex-element (fixed emas), shuning
            uchun klaviatura ochilganda hech qachon siljimaydi. Pastki qismi
            iOS Home Indicator ostida qolib ketmasligi uchun xavfsiz hudud
            (safe-area) bo'shlig'i qo'shilgan. */}
        <nav className="flex flex-shrink-0 border-t border-h-border bg-h-surface pb-[env(safe-area-inset-bottom)] lg:hidden">
          {mobileNavItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);
            const isHome = item.href === homeItem.href;

            if (isHome) {
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex flex-1 items-center justify-center py-3.5"
                  aria-label={item.label}
                >
                  <span
                    className={`flex h-9 w-9 items-center justify-center rounded-full ${
                      active ? "bg-h-accent text-white" : "text-h-muted"
                    }`}
                  >
                    <span className={`inline-flex ${active ? "animate-nav-icon-in" : ""}`}>
                      <Icon size={26} strokeWidth={2} />
                    </span>
                  </span>
                </Link>
              );
            }

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-label={item.label}
                className="flex flex-1 items-center justify-center py-3.5"
              >
                <span
                  className={`flex h-9 w-9 items-center justify-center rounded-full ${
                    active ? "bg-h-accent text-white" : "text-h-muted"
                  }`}
                >
                  <span className={`inline-flex ${active ? "animate-nav-icon-in" : ""}`}>
                    <Icon size={20} strokeWidth={2} />
                  </span>
                </span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
