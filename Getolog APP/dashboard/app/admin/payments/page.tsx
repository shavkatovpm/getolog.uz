"use client";

import { useEffect, useState } from "react";
import { Check, X } from "lucide-react";
import { PaymentRow, apiFetch } from "@/lib/api";
import { useChannels } from "@/lib/channel-context";
import { ReceiptImage } from "@/components/ReceiptImage";
import { Select } from "@/components/Select";
import { PageLoader } from "@/components/PageLoader";
import { useLogoGatedLoading } from "@/lib/logo-gate";

const STATUS_LABELS: Record<string, string> = {
  pending: "Kutilmoqda",
  approved: "Tasdiqlangan",
  rejected: "Rad etilgan",
};

const STATUS_BADGE: Record<string, string> = {
  pending: "bg-h-warning/10 text-h-warning",
  approved: "bg-h-success/10 text-h-success",
  rejected: "bg-h-danger/10 text-h-danger",
};

type Tab = "pending" | "approved" | "rejected" | "all";

const TABS: [Tab, string][] = [
  ["pending", "Kutilayotgan"],
  ["approved", "Tasdiqlangan"],
  ["rejected", "Rad etilgan"],
  ["all", "Hammasi"],
];

export default function PaymentsPage() {
  const { selectedChannel, loading: channelsLoading } = useChannels();
  const [tab, setTab] = useState<Tab>("pending");
  const [payments, setPayments] = useState<PaymentRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const gatedLoading = useLogoGatedLoading(channelsLoading || loading);

  async function loadPayments(activeTab: Tab) {
    try {
      const qs = activeTab === "all" ? "" : `?status=${activeTab}`;
      const data = await apiFetch<PaymentRow[]>(`/api/payments${qs}`);
      setPayments(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Yuklashda xatolik");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    void loadPayments(tab);
  }, [tab]);

  async function decidePayment(paymentId: number, action: "approve" | "reject") {
    try {
      await apiFetch(`/api/payments/${paymentId}/${action}`, { method: "POST" });
      await loadPayments(tab);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Amalni bajarishda xatolik");
    }
  }

  if (gatedLoading || !selectedChannel) return <PageLoader />;

  const channelPayments = payments.filter((p) => p.channel_id === selectedChannel.id);

  return (
    <div>
      <h1 className="mb-4 text-lg font-medium text-h-ink">To&apos;lovlar</h1>

      {/* Mobil: dropdown, joy tejash uchun */}
      <Select
        value={tab}
        onChange={(e) => setTab(e.target.value as Tab)}
        aria-label="Holat bo'yicha filtr"
        wrapperClassName="mb-4 w-full sm:hidden"
        className="w-full py-1.5 pl-2 text-sm"
      >
        {TABS.map(([key, label]) => (
          <option key={key} value={key}>
            {label}
          </option>
        ))}
      </Select>

      {/* Desktop: tab-tugmalar */}
      <div className="mb-4 hidden flex-wrap gap-1.5 sm:flex">
        {TABS.map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              tab === key ? "bg-h-accent text-white" : "border border-h-border text-h-muted hover:bg-h-surface"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {error && (
        <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      )}

      {channelPayments.length === 0 ? (
        <p className="text-sm text-h-muted">Bu bo&apos;limda to&apos;lov yo&apos;q.</p>
      ) : (
        <ul className="space-y-3">
          {channelPayments.map((p) => (
            <li key={p.id} className="rounded-lg border border-h-border bg-h-surface p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="text-sm">
                  <div className="flex items-center gap-2 text-h-ink">
                    {p.subscriber_full_name ?? `Obunachi ID: ${p.user_id}`}
                    {p.subscriber_username && (
                      <span className="text-h-muted">@{p.subscriber_username}</span>
                    )}
                    {p.status !== "pending" && (
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_BADGE[p.status]}`}>
                        {STATUS_LABELS[p.status] ?? p.status}
                      </span>
                    )}
                  </div>
                  <div className="text-h-muted">
                    {p.amount.toLocaleString()} so&apos;m — {new Date(p.created_at).toLocaleString()}
                  </div>
                </div>
                {p.status === "pending" && (
                  <div className="flex gap-1.5">
                    <button
                      onClick={() => decidePayment(p.id, "approve")}
                      aria-label="Tasdiqlash"
                      className="flex h-8 w-8 items-center justify-center rounded-md bg-h-success/10 text-h-success transition-colors hover:bg-h-success/20"
                    >
                      <Check size={16} strokeWidth={2.5} />
                    </button>
                    <button
                      onClick={() => decidePayment(p.id, "reject")}
                      aria-label="Rad etish"
                      className="flex h-8 w-8 items-center justify-center rounded-md bg-h-danger/10 text-h-danger transition-colors hover:bg-h-danger/20"
                    >
                      <X size={16} strokeWidth={2.5} />
                    </button>
                  </div>
                )}
              </div>
              {p.has_receipt && <ReceiptImage paymentId={p.id} />}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
