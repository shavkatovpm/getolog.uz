"use client";

import { useEffect, useState } from "react";
import { SubscriberRow, apiFetch } from "@/lib/api";
import { useChannels } from "@/lib/channel-context";

const STATUS_LABELS: Record<string, string> = {
  active: "Faol",
  expired: "Muddati tugagan",
  removed: "Chiqarilgan",
};

export default function SubscribersPage() {
  const { selectedChannel } = useChannels();
  const [subscribers, setSubscribers] = useState<SubscriberRow[]>([]);

  useEffect(() => {
    if (!selectedChannel) return;
    void apiFetch<SubscriberRow[]>(`/api/channels/${selectedChannel.id}/subscribers`).then(
      setSubscribers
    );
  }, [selectedChannel]);

  if (!selectedChannel) return null;

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">Obunachilar</h1>

      {subscribers.length === 0 ? (
        <p className="text-sm text-h-muted">Hali obunachilar yo&apos;q.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-h-border bg-h-surface">
          <table className="min-w-full divide-y divide-h-border text-sm">
            <thead className="text-left">
              <tr>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                  User ID
                </th>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                  Holat
                </th>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                  Tugash sanasi
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-h-border">
              {subscribers.map((s) => (
                <tr key={s.id}>
                  <td className="px-4 py-3 text-h-ink">{s.user_id}</td>
                  <td className="px-4 py-3 text-h-muted">{STATUS_LABELS[s.status] ?? s.status}</td>
                  <td className="px-4 py-3 text-h-muted">{s.end_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
