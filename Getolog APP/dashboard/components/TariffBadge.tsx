"use client";

import { daysUntil, tariffUrgency } from "@/lib/tariff";
import { useMe } from "@/lib/me-context";

const DOT_TONE: Record<string, string> = {
  expired: "bg-h-danger",
  urgent: "bg-h-danger",
  soon: "bg-h-warning",
  safe: "bg-h-success",
};

const TEXT_TONE: Record<string, string> = {
  expired: "text-h-danger",
  urgent: "text-h-danger",
  soon: "text-h-warning",
  safe: "text-h-muted",
};

/** Navbar'da doim ko'rinadigan ixcham tarif indikatori — batafsili Bosh sahifadagi kartochkada. */
export function TariffBadge() {
  const { me } = useMe();
  if (!me?.tariff_plan) return null;

  let urgency: keyof typeof DOT_TONE = "safe";
  let label: string;

  if (me.tariff_expiry) {
    const daysLeft = daysUntil(me.tariff_expiry);
    urgency = tariffUrgency(daysLeft);
    label = daysLeft <= 0 ? "Tarif tugagan" : `${daysLeft} kun qoldi`;
  } else if (me.limit_exceeded_at) {
    urgency = "soon";
    label = "Limit oshgan";
  } else {
    label = me.tariff_label ?? "Bepul tarif";
  }

  return (
    <div className="flex items-center gap-1.5 rounded-md border border-h-border px-2.5 py-1.5 text-xs">
      <span className={`h-1.5 w-1.5 flex-shrink-0 rounded-full ${DOT_TONE[urgency]}`} />
      <span className={`whitespace-nowrap font-medium ${TEXT_TONE[urgency]}`}>{label}</span>
    </div>
  );
}
