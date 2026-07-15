"use client";

import { useChannels } from "@/lib/channel-context";

export default function AdminOverviewPage() {
  const { selectedChannel } = useChannels();
  if (!selectedChannel) return null;

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">{selectedChannel.title}</h1>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <StatCard label="Faol obunachi" value={selectedChannel.active_subscribers} />
        <StatCard label="Oylik daromad" value={selectedChannel.monthly_revenue.toLocaleString()} />
        <StatCard
          label="Bot huquqlari"
          value={selectedChannel.permissions_ok ? "OK" : "Yetarli emas"}
          tone={selectedChannel.permissions_ok ? "success" : "danger"}
        />
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string | number;
  tone?: "default" | "success" | "danger";
}) {
  const toneClass =
    tone === "success" ? "text-h-success" : tone === "danger" ? "text-h-danger" : "text-h-ink";
  return (
    <div className="rounded-lg border border-h-border bg-h-surface p-4">
      <div className="text-xs font-medium tracking-wide text-h-muted uppercase">{label}</div>
      <div className={`text-xl font-medium ${toneClass}`}>{value}</div>
    </div>
  );
}
