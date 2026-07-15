"use client";

import { useEffect, useState } from "react";
import { AdminRow, apiFetch } from "@/lib/api";

const TARIFF_OPTIONS = [
  { value: "free", label: "Bepul (sinov)" },
  { value: "start", label: "Start — $50" },
  { value: "pro", label: "Pro — $100" },
  { value: "business", label: "Biznes — $150" },
  { value: "scale", label: "Scale" },
];

export default function OwnerAdminsPage() {
  const [admins, setAdmins] = useState<AdminRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formState, setFormState] = useState<Record<number, { tariff: string; months: string }>>({});
  const [savingId, setSavingId] = useState<number | null>(null);

  useEffect(() => {
    void loadAdmins();
  }, []);

  async function loadAdmins() {
    setLoading(true);
    try {
      const data = await apiFetch<AdminRow[]>("/api/admins");
      setAdmins(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Yuklashda xatolik");
    } finally {
      setLoading(false);
    }
  }

  async function submitTariff(adminId: number) {
    const form = formState[adminId] ?? { tariff: "start", months: "1" };
    setSavingId(adminId);
    try {
      await apiFetch(`/api/admins/${adminId}/tariff`, {
        method: "POST",
        body: JSON.stringify({ tariff_plan: form.tariff, months: Number(form.months) }),
      });
      await loadAdmins();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Saqlashda xatolik");
    } finally {
      setSavingId(null);
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">Adminlar</h1>

      {error && (
        <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-h-muted">Yuklanmoqda...</p>
      ) : admins.length === 0 ? (
        <p className="text-sm text-h-muted">Hali birorta ham admin ro&apos;yxatdan o&apos;tmagan.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-h-border bg-h-surface">
          <table className="min-w-full divide-y divide-h-border text-sm">
            <thead className="text-left">
              <tr>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">Ism</th>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">Tarif</th>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">Muddat</th>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                  Faol / Umrbod
                </th>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                  Yangi tarif berish
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-h-border">
              {admins.map((admin) => {
                const form = formState[admin.id] ?? { tariff: "start", months: "1" };
                return (
                  <tr key={admin.id}>
                    <td className="px-4 py-3">
                      <div className="font-medium text-h-ink">{admin.full_name}</div>
                      <div className="text-xs text-h-muted">{admin.telegram_id}</div>
                    </td>
                    <td className="px-4 py-3 text-h-ink">{admin.tariff_label}</td>
                    <td className="px-4 py-3 text-h-muted">{admin.tariff_expiry ?? "—"}</td>
                    <td className="px-4 py-3 text-h-ink">
                      {admin.active_subscribers} / {admin.lifetime_subscribers}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <select
                          value={form.tariff}
                          onChange={(e) =>
                            setFormState((prev) => ({
                              ...prev,
                              [admin.id]: { ...form, tariff: e.target.value },
                            }))
                          }
                          className="rounded-md border border-h-border bg-h-surface px-2 py-1 text-h-ink"
                        >
                          {TARIFF_OPTIONS.map((opt) => (
                            <option key={opt.value} value={opt.value}>
                              {opt.label}
                            </option>
                          ))}
                        </select>
                        <input
                          type="number"
                          min={1}
                          value={form.months}
                          onChange={(e) =>
                            setFormState((prev) => ({
                              ...prev,
                              [admin.id]: { ...form, months: e.target.value },
                            }))
                          }
                          className="w-16 rounded-md border border-h-border bg-h-surface px-2 py-1 text-h-ink"
                        />
                        <span className="text-h-muted">oy</span>
                        <button
                          onClick={() => submitTariff(admin.id)}
                          disabled={savingId === admin.id}
                          className="rounded-md bg-h-accent px-3 py-1 text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                        >
                          {savingId === admin.id ? "..." : "Belgilash"}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
