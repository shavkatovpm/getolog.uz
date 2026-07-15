"use client";

import { useEffect, useState } from "react";
import { OverviewStats, apiFetch } from "@/lib/api";

export default function OwnerOverviewPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<OverviewStats>("/api/stats/overview")
      .then(setStats)
      .catch((err) => setError(err instanceof Error ? err.message : "Yuklashda xatolik"));
  }, []);

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">Statistika</h1>

      {error && (
        <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      )}

      {!stats ? (
        <p className="text-sm text-h-muted">Yuklanmoqda...</p>
      ) : (
        <>
          <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <StatCard label="Adminlar" value={stats.total_admins} />
            <StatCard label="Kanallar" value={stats.total_channels} />
            <StatCard label="Faol obunachilar" value={stats.total_active_subscribers} />
            <StatCard
              label="30 kunlik to'lov hajmi"
              value={stats.total_revenue_30d.toLocaleString()}
            />
          </div>

          <div className="rounded-lg border border-h-border bg-h-surface p-5">
            <h2 className="mb-3 text-xs font-medium tracking-wide text-h-muted uppercase">
              Tarifi tez orada tugaydigan adminlar (3 kun ichida)
            </h2>
            {stats.expiring_admins.length === 0 ? (
              <p className="text-sm text-h-muted">Hozircha yo&apos;q.</p>
            ) : (
              <ul className="divide-y divide-h-border rounded-md border border-h-border">
                {stats.expiring_admins.map((a) => (
                  <li key={a.id} className="flex items-center justify-between p-3 text-sm">
                    <div>
                      <div className="font-medium text-h-ink">{a.full_name}</div>
                      <div className="text-xs text-h-muted">{a.telegram_id}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-h-ink">{a.tariff_label}</div>
                      <div
                        className={`text-xs ${a.days_left <= 1 ? "text-h-danger" : "text-h-muted"}`}
                      >
                        {a.days_left <= 0
                          ? "bugun tugaydi"
                          : `${a.days_left} kundan keyin tugaydi`}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-h-border bg-h-surface p-4">
      <div className="text-xs font-medium tracking-wide text-h-muted uppercase">{label}</div>
      <div className="text-xl font-medium text-h-ink">{value}</div>
    </div>
  );
}
