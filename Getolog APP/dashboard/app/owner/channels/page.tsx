"use client";

import { useEffect, useState } from "react";
import { ChannelRow, apiFetch } from "@/lib/api";

export default function OwnerChannelsPage() {
  const [channels, setChannels] = useState<ChannelRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<ChannelRow[]>("/api/channels")
      .then(setChannels)
      .catch((err) => setError(err instanceof Error ? err.message : "Yuklashda xatolik"))
      .finally(() => setLoading(false));
  }, []);

  const totalActive = channels.reduce((sum, c) => sum + c.active_subscribers, 0);

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">Kanallar</h1>

      {error && (
        <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-h-muted">Yuklanmoqda...</p>
      ) : channels.length === 0 ? (
        <p className="text-sm text-h-muted">Hali birorta ham kanal ulanmagan.</p>
      ) : (
        <>
          <div className="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-h-border bg-h-surface p-4">
              <div className="text-xs font-medium tracking-wide text-h-muted uppercase">
                Jami kanal
              </div>
              <div className="text-xl font-medium text-h-ink">{channels.length}</div>
            </div>
            <div className="rounded-lg border border-h-border bg-h-surface p-4">
              <div className="text-xs font-medium tracking-wide text-h-muted uppercase">
                Jami faol obunachi
              </div>
              <div className="text-xl font-medium text-h-ink">{totalActive}</div>
            </div>
          </div>

          <div className="overflow-x-auto rounded-lg border border-h-border bg-h-surface">
            <table className="min-w-full divide-y divide-h-border text-sm">
              <thead className="text-left">
                <tr>
                  <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                    Kanal
                  </th>
                  <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                    Admin
                  </th>
                  <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                    Faol obunachi
                  </th>
                  <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                    Bot huquqlari
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-h-border">
                {channels.map((c) => (
                  <tr key={c.id}>
                    <td className="px-4 py-3 font-medium text-h-ink">{c.title}</td>
                    <td className="px-4 py-3 text-h-muted">{c.admin_full_name}</td>
                    <td className="px-4 py-3 text-h-ink">{c.active_subscribers}</td>
                    <td className={`px-4 py-3 ${c.permissions_ok ? "text-h-success" : "text-h-danger"}`}>
                      {c.permissions_ok ? "OK" : "Yetarli emas"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
