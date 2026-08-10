"use client";

import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import Link from "next/link";
import { TriangleAlert, X } from "lucide-react";
import { useChannels } from "@/lib/channel-context";
import { useMe } from "@/lib/me-context";
import { apiFetch, ChannelGrowth, getChannelGrowth, MeInfo, PaymentRow } from "@/lib/api";
import {
  computeTariffUsage,
  daysUntil,
  formatDate,
  TariffUsage,
  TARIFF_SUPPORT_URL,
  UsageTone,
} from "@/lib/tariff";
import {
  buildGrowthSeries,
  defaultGrowthWindow,
  GROWTH_WINDOW_LABELS,
  GrowthWindowOption,
} from "@/lib/growth";
import { GrowthChart } from "@/components/GrowthChart";
import { Select } from "@/components/Select";
import { PageLoader } from "@/components/PageLoader";
import { useLogoGatedLoading } from "@/lib/logo-gate";

export default function AdminOverviewPage() {
  const { selectedChannel, loading: channelsLoading } = useChannels();
  const { me } = useMe();
  const [growthData, setGrowthData] = useState<ChannelGrowth | null>(null);
  const [windowOption, setWindowOption] = useState<GrowthWindowOption | null>(null);
  const [pendingCount, setPendingCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  // Kanal ma'lumotlari HAM shu bitta loader ichida hisobga olinadi — aks
  // holda sahifa ochilganda avval qatlamdagi (layout) loader, so'ng shu
  // yerdagi alohida loader ketma-ket chiqib, chizish animatsiyasi qayta
  // boshlanib qolardi.
  const gatedLoading = useLogoGatedLoading(channelsLoading || loading);

  useEffect(() => {
    if (!selectedChannel) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setGrowthData(null);
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setWindowOption(null);
    const channelId = selectedChannel.id;

    const growthPromise = getChannelGrowth(channelId)
      .then((data) => {
        setGrowthData(data);
        setWindowOption(defaultGrowthWindow(data.channel_created_at));
      })
      .catch(() => {
        /* grafik ixtiyoriy — yuklanmasa shunchaki ko'rsatilmaydi */
      });

    const pendingPromise = apiFetch<PaymentRow[]>("/api/payments?status=pending")
      .then((payments) => {
        setPendingCount(payments.filter((p) => p.channel_id === channelId).length);
      })
      .catch(() => {
        /* ixtiyoriy — yuklanmasa karta ko'rsatilmaydi */
      });

    Promise.allSettled([growthPromise, pendingPromise]).then(() => setLoading(false));
  }, [selectedChannel]);

  const growth = useMemo(() => {
    if (!growthData || !windowOption) return null;
    return buildGrowthSeries(growthData.channel_created_at, growthData.joins, windowOption);
  }, [growthData, windowOption]);

  if (gatedLoading) return <PageLoader />;
  if (!selectedChannel) return null;

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">{selectedChannel.title}</h1>

      {!selectedChannel.permissions_ok && (
        <div className="animate-card-in mb-6 flex items-start gap-3 rounded-lg border border-h-danger/25 bg-h-danger/5 p-4">
          <TriangleAlert size={18} className="mt-0.5 flex-shrink-0 text-h-danger" />
          <div>
            <div className="text-sm font-medium text-h-danger">Bot kanalda yetarli huquqqa ega emas</div>
            <p className="mt-1 text-xs text-h-muted">
              Obunachilarni qabul qilish va chiqarish to&apos;xtab qolishi mumkin. Telegram
              kanalida → Administratorlar → botni tahrirlang va quyidagilarni yoqing: taklif
              havolasi yaratish, a&apos;zolarni cheklash, xabar yuborish, xabar o&apos;chirish.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Faol obunachi" value={selectedChannel.active_subscribers} delayMs={0} />
        <StatCard
          label="Oylik daromad"
          value={selectedChannel.monthly_revenue.toLocaleString()}
          delayMs={40}
        />
        <StatCard
          label="Bot huquqlari"
          value={selectedChannel.permissions_ok ? "OK" : "Yetarli emas"}
          tone={selectedChannel.permissions_ok ? "success" : "danger"}
          delayMs={80}
        />
        {pendingCount !== null && (
          <StatCard
            label="Kutilayotgan to'lov"
            value={pendingCount}
            tone={pendingCount > 0 ? "warning" : "default"}
            href="/admin/payments"
            delayMs={120}
          />
        )}
      </div>

      {growth && windowOption && (
        <GrowthCard growth={growth} windowOption={windowOption} onWindowChange={setWindowOption} />
      )}

      {me && <TariffCountdown me={me} />}
    </div>
  );
}

function GrowthCard({
  growth,
  windowOption,
  onWindowChange,
}: {
  growth: ReturnType<typeof buildGrowthSeries>;
  windowOption: GrowthWindowOption;
  onWindowChange: (option: GrowthWindowOption) => void;
}) {
  const delta = growth.endValue - growth.startValue;
  return (
    <div
      className="animate-card-in mt-6 rounded-lg border border-h-border bg-h-surface p-4"
      style={{ animationDelay: "160ms" }}
    >
      <div className="mb-3 flex items-baseline justify-between">
        <div>
          <h2 className="text-sm font-medium text-h-ink">Obunachilar o&apos;sishi</h2>
          <Select
            value={windowOption}
            onChange={(e) => onWindowChange(e.target.value as GrowthWindowOption)}
            aria-label="Grafik davri"
            className="mt-1 py-0.5 pl-1.5 text-xs text-h-muted"
          >
            {(Object.keys(GROWTH_WINDOW_LABELS) as GrowthWindowOption[]).map((opt) => (
              <option key={opt} value={opt}>
                {GROWTH_WINDOW_LABELS[opt]}
              </option>
            ))}
          </Select>
        </div>
        <div className="text-right">
          <div className="text-lg font-medium text-h-ink">{growth.endValue}</div>
          <div className={`text-xs font-medium ${delta >= 0 ? "text-h-success" : "text-h-danger"}`}>
            {delta >= 0 ? "+" : ""}
            {delta} shu davrda
          </div>
        </div>
      </div>
      <GrowthChart series={growth} />
    </div>
  );
}

const TONE_BORDER: Record<UsageTone, string> = {
  danger: "border-h-danger/25 bg-h-danger/5",
  warning: "border-h-warning/25 bg-h-warning/5",
  safe: "border-h-success/25 bg-h-success/5",
};
const TONE_BG: Record<UsageTone, string> = {
  danger: "bg-h-danger",
  warning: "bg-h-warning",
  safe: "bg-h-success",
};
const TONE_TEXT: Record<UsageTone, string> = {
  danger: "text-h-danger",
  warning: "text-h-warning",
  safe: "text-h-success",
};

function UsageRow({
  label,
  detail,
  percent,
  active,
}: {
  label: string;
  detail: string;
  percent: number;
  active: boolean;
}) {
  const tone: UsageTone = percent > 70 ? "danger" : percent >= 50 ? "warning" : "safe";
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="flex items-center gap-1.5 font-medium text-h-ink">
          {label}
          {active && (
            <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-medium text-white ${TONE_BG[tone]}`}>
              asosiy
            </span>
          )}
        </span>
        <span className="text-h-muted">{detail}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-h-border">
        <div
          className={`h-full rounded-full transition-[width] duration-500 ${TONE_BG[tone]}`}
          style={{ width: `${Math.max(0, Math.min(100, percent))}%` }}
        />
      </div>
    </div>
  );
}

function TariffCountdown({ me }: { me: MeInfo }) {
  const [detailOpen, setDetailOpen] = useState(false);

  const hasExpiry = !!me.tariff_expiry;
  const daysLeft = me.tariff_expiry ? daysUntil(me.tariff_expiry) : null;
  const expired = daysLeft !== null && daysLeft <= 0;

  const usage: TariffUsage | null = computeTariffUsage({
    tariffStartedAt: me.tariff_started_at,
    tariffExpiry: me.tariff_expiry,
    subscriberCount: me.subscriber_count,
    subscriberLimit: me.subscriber_limit,
  });

  let tone: UsageTone = usage?.tone ?? (expired ? "danger" : "safe");
  if (!hasExpiry && me.limit_exceeded_at) tone = "warning";

  return (
    <button
      type="button"
      onClick={() => setDetailOpen(true)}
      className={`animate-card-in mt-6 w-full rounded-lg border p-4 text-left transition-colors hover:bg-h-bg ${TONE_BORDER[tone]}`}
      style={{ animationDelay: "200ms" }}
    >
      <div className="mb-4 flex items-center gap-4">
        <div
          className={`flex h-14 w-14 flex-shrink-0 flex-col items-center justify-center rounded-full text-white ${TONE_BG[tone]}`}
        >
          {hasExpiry ? (
            <>
              <span className="text-lg font-semibold leading-none">{expired ? "!" : daysLeft}</span>
              {!expired && <span className="text-[9px] leading-none opacity-80">kun</span>}
            </>
          ) : (
            <span className="text-lg font-semibold leading-none">∞</span>
          )}
        </div>
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-h-muted">
            Tarif — {me.tariff_label}
          </div>
          <div className={`text-sm font-medium ${TONE_TEXT[tone]}`}>
            {hasExpiry
              ? expired
                ? `Muddati ${Math.abs(daysLeft!)} kun oldin tugagan`
                : daysLeft === 0
                  ? "Bugun tugaydi"
                  : `${daysLeft} kundan so'ng tugaydi`
              : me.limit_exceeded_at
                ? "Obunachi limiti oshib ketgan (eslatma)"
                : "Muddatsiz (bepul tarif)"}
          </div>
          <div className="text-xs text-h-muted">
            {hasExpiry ? formatDate(me.tariff_expiry!) : `${me.subscriber_count ?? 0} / ${me.subscriber_limit ?? "cheksiz"} obunachi`}
          </div>
        </div>
      </div>

      {usage && (
        <div className="space-y-3 border-t border-h-border pt-4">
          {usage.daysPercent !== null && (
            <UsageRow
              label="Kun bo'yicha"
              detail={`${Math.round(usage.daysPercent)}%`}
              percent={usage.daysPercent}
              active={usage.dominantMetric === "days"}
            />
          )}
          {usage.subscribersPercent !== null && (
            <UsageRow
              label="Obunachi bo'yicha"
              detail={`${me.subscriber_count} / ${me.subscriber_limit}`}
              percent={usage.subscribersPercent}
              active={usage.dominantMetric === "subscribers"}
            />
          )}
          <p className="text-[11px] text-h-muted">
            Navbar'dagi chiziq ikkalasining yuqorirog'idan hisoblanadi — hozir{" "}
            {usage.dominantMetric === "days" ? "kunlar" : "obunachilar soni"} yetakchi.
          </p>
        </div>
      )}

      {detailOpen && (
        <TariffDetailModal me={me} onClose={() => setDetailOpen(false)} />
      )}
    </button>
  );
}

function TariffDetailModal({ me, onClose }: { me: MeInfo; onClose: () => void }) {
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const daysLeft = me.tariff_expiry ? daysUntil(me.tariff_expiry) : null;

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={(e) => e.stopPropagation()}
    >
      <button
        type="button"
        aria-label="Yopish"
        onClick={onClose}
        className="animate-modal-backdrop absolute inset-0 bg-black/50"
      />
      <div className="animate-modal-panel relative w-full max-w-sm rounded-lg border border-h-border bg-h-surface p-5 shadow-xl">
        <button
          type="button"
          aria-label="Yopish"
          onClick={onClose}
          className="absolute top-3 right-3 flex h-7 w-7 items-center justify-center rounded-md text-h-muted transition-colors hover:bg-h-bg hover:text-h-ink"
        >
          <X size={16} />
        </button>
        <h2 className="mb-1 pr-6 text-sm font-medium text-h-ink">Tarif haqida to&apos;liq ma&apos;lumot</h2>
        <p className="mb-4 text-xs text-h-muted">{me.tariff_label}</p>

        <div className="mb-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-h-muted">Muddati</span>
            <span className="text-h-ink">{me.tariff_expiry ? formatDate(me.tariff_expiry) : "—"}</span>
          </div>
          {daysLeft !== null && (
            <div className="flex justify-between">
              <span className="text-h-muted">Qolgan kun</span>
              <span className="text-h-ink">{daysLeft > 0 ? `${daysLeft} kun` : "Tugagan"}</span>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-h-muted">Obunachilar</span>
            <span className="text-h-ink">
              {me.subscriber_count ?? "—"} / {me.subscriber_limit ?? "cheksiz"}
            </span>
          </div>
        </div>

        {me.limit_exceeded_at && (
          <div className="mb-4 rounded-md border border-h-warning/25 bg-h-warning/5 px-3 py-2 text-xs text-h-warning">
            Obunachilar soni limitdan oshib ketdi — bu shunchaki eslatma, bot ishlashda
            davom etadi. Ko&apos;proq obunachi qabul qilish uchun tarifingizni oshirishingiz mumkin.
          </div>
        )}

        <a
          href={TARIFF_SUPPORT_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 rounded-md bg-h-accent px-3 py-2 text-sm text-white transition-opacity hover:opacity-90"
        >
          Tarifni oshirish uchun murojaat qilish
        </a>
      </div>
    </div>,
    document.body,
  );
}

function StatCard({
  label,
  value,
  tone = "default",
  href,
  delayMs = 0,
}: {
  label: string;
  value: string | number;
  tone?: "default" | "success" | "danger" | "warning";
  href?: string;
  delayMs?: number;
}) {
  const toneClass =
    tone === "success"
      ? "text-h-success"
      : tone === "danger"
        ? "text-h-danger"
        : tone === "warning"
          ? "text-h-warning"
          : "text-h-ink";
  const borderClass = tone === "warning" ? "border-h-warning/40" : "border-h-border";
  const style = { animationDelay: `${delayMs}ms` };

  const content = (
    <>
      <div className="text-xs font-medium tracking-wide text-h-muted uppercase">{label}</div>
      <div className={`text-xl font-medium ${toneClass}`}>{value}</div>
    </>
  );

  if (href) {
    return (
      <Link
        href={href}
        style={style}
        className={`animate-card-in rounded-lg border bg-h-surface p-4 transition-colors hover:bg-h-bg ${borderClass}`}
      >
        {content}
      </Link>
    );
  }

  return (
    <div style={style} className={`animate-card-in rounded-lg border bg-h-surface p-4 ${borderClass}`}>
      {content}
    </div>
  );
}
