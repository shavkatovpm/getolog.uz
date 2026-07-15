"use client";

import { useEffect, useState } from "react";
import { PaymentRow, apiFetch } from "@/lib/api";

const STATUS_LABELS: Record<string, string> = {
  pending: "Kutilmoqda",
  approved: "Tasdiqlangan",
  rejected: "Rad etilgan",
};

const STATUS_TONE: Record<string, string> = {
  pending: "text-h-muted",
  approved: "text-h-success",
  rejected: "text-h-danger",
};

export default function OwnerPaymentsPage() {
  const [payments, setPayments] = useState<PaymentRow[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Filtr o'zgarganda ro'yxatni qayta yuklaydi, shu payt "Yuklanmoqda..." ko'rsatiladi.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    const query = statusFilter ? `?status=${statusFilter}` : "";
    apiFetch<PaymentRow[]>(`/api/payments${query}`)
      .then(setPayments)
      .catch((err) => setError(err instanceof Error ? err.message : "Yuklashda xatolik"))
      .finally(() => setLoading(false));
  }, [statusFilter]);

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-medium text-h-ink">To&apos;lovlar tarixi</h1>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-md border border-h-border bg-h-surface px-2 py-1.5 text-sm text-h-ink"
        >
          <option value="">Barchasi</option>
          <option value="pending">Kutilmoqda</option>
          <option value="approved">Tasdiqlangan</option>
          <option value="rejected">Rad etilgan</option>
        </select>
      </div>

      {error && (
        <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-h-muted">Yuklanmoqda...</p>
      ) : payments.length === 0 ? (
        <p className="text-sm text-h-muted">To&apos;lovlar topilmadi.</p>
      ) : (
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
                  Summa
                </th>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                  Holat
                </th>
                <th className="px-4 py-3 text-xs font-medium tracking-wide text-h-muted uppercase">
                  Sana
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-h-border">
              {payments.map((p) => (
                <tr key={p.id}>
                  <td className="px-4 py-3 text-h-ink">{p.channel_title}</td>
                  <td className="px-4 py-3 text-h-muted">{p.admin_full_name}</td>
                  <td className="px-4 py-3 text-h-ink">{p.amount.toLocaleString()}</td>
                  <td className={`px-4 py-3 ${STATUS_TONE[p.status] ?? "text-h-muted"}`}>
                    {STATUS_LABELS[p.status] ?? p.status}
                  </td>
                  <td className="px-4 py-3 text-h-muted">
                    {new Date(p.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
