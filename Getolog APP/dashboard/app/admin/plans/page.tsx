"use client";

import { useEffect, useState } from "react";
import { PlanRow, apiFetch } from "@/lib/api";
import { useChannels } from "@/lib/channel-context";

export default function PlansPage() {
  const { selectedChannel } = useChannels();
  const [plans, setPlans] = useState<PlanRow[]>([]);
  const [newPlan, setNewPlan] = useState({ duration_months: "1", price: "" });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedChannel) return;
    void apiFetch<PlanRow[]>(`/api/plans?channel_id=${selectedChannel.id}`).then(setPlans);
  }, [selectedChannel]);

  async function addPlan() {
    if (!selectedChannel) return;
    try {
      await apiFetch("/api/plans", {
        method: "POST",
        body: JSON.stringify({
          channel_id: selectedChannel.id,
          duration_months: Number(newPlan.duration_months),
          price: Number(newPlan.price),
        }),
      });
      setNewPlan({ duration_months: "1", price: "" });
      const updated = await apiFetch<PlanRow[]>(`/api/plans?channel_id=${selectedChannel.id}`);
      setPlans(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Tarif qo'shishda xatolik");
    }
  }

  if (!selectedChannel) return null;

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">Tarif rejalari</h1>

      {error && (
        <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      )}

      <div className="rounded-lg border border-h-border bg-h-surface p-5">
        <ul className="mb-4 divide-y divide-h-border rounded-md border border-h-border">
          {plans.length === 0 && (
            <li className="p-3 text-sm text-h-muted">Hali tarif qo&apos;shilmagan</li>
          )}
          {plans.map((p) => (
            <li key={p.id} className="flex justify-between p-3 text-sm">
              <span className="text-h-ink">
                {p.duration_months} oy — {p.price.toLocaleString()} {p.currency}
              </span>
              <span className={p.active ? "text-h-success" : "text-h-muted"}>
                {p.active ? "faol" : "faol emas"}
              </span>
            </li>
          ))}
        </ul>

        <div className="flex flex-wrap items-center gap-2">
          <input
            type="number"
            min={1}
            value={newPlan.duration_months}
            onChange={(e) => setNewPlan((p) => ({ ...p, duration_months: e.target.value }))}
            className="w-16 rounded-md border border-h-border bg-h-surface px-2 py-1 text-h-ink"
          />
          <span className="text-sm text-h-muted">oy —</span>
          <input
            type="number"
            min={1}
            placeholder="narx (so'm)"
            value={newPlan.price}
            onChange={(e) => setNewPlan((p) => ({ ...p, price: e.target.value }))}
            className="w-32 rounded-md border border-h-border bg-h-surface px-2 py-1 text-h-ink"
          />
          <button
            onClick={addPlan}
            className="rounded-md bg-h-accent px-3 py-1 text-sm text-white transition-opacity hover:opacity-90"
          >
            Qo&apos;shish
          </button>
        </div>
      </div>
    </div>
  );
}
