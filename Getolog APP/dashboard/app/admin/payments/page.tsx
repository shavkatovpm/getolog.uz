"use client";

import { useEffect, useState } from "react";
import { PaymentRow, apiFetch } from "@/lib/api";
import { useChannels } from "@/lib/channel-context";
import { ReceiptImage } from "@/components/ReceiptImage";

export default function PaymentsPage() {
  const { selectedChannel } = useChannels();
  const [payments, setPayments] = useState<PaymentRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadPayments() {
    try {
      const data = await apiFetch<PaymentRow[]>("/api/payments?status=pending");
      setPayments(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Yuklashda xatolik");
    }
  }

  useEffect(() => {
    // Mount bo'lganda kutilayotgan to'lovlarni yuklaydi.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadPayments();
  }, []);

  async function decidePayment(paymentId: number, action: "approve" | "reject") {
    try {
      await apiFetch(`/api/payments/${paymentId}/${action}`, { method: "POST" });
      await loadPayments();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Amalni bajarishda xatolik");
    }
  }

  if (!selectedChannel) return null;

  const channelPayments = payments.filter((p) => p.channel_id === selectedChannel.id);

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">Kutilayotgan to&apos;lovlar</h1>

      {error && (
        <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      )}

      {channelPayments.length === 0 ? (
        <p className="text-sm text-h-muted">Hozircha kutilayotgan to&apos;lov yo&apos;q.</p>
      ) : (
        <ul className="space-y-3">
          {channelPayments.map((p) => (
            <li key={p.id} className="rounded-lg border border-h-border bg-h-surface p-4">
              <div className="flex items-center justify-between">
                <div className="text-sm">
                  <div className="text-h-ink">Obunachi ID: {p.user_id}</div>
                  <div className="text-h-muted">
                    {p.amount.toLocaleString()} so&apos;m — {new Date(p.created_at).toLocaleString()}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => decidePayment(p.id, "approve")}
                    className="rounded-md bg-h-success px-3 py-1 text-sm text-white transition-opacity hover:opacity-90"
                  >
                    Tasdiqlash
                  </button>
                  <button
                    onClick={() => decidePayment(p.id, "reject")}
                    className="rounded-md bg-h-danger px-3 py-1 text-sm text-white transition-opacity hover:opacity-90"
                  >
                    Rad etish
                  </button>
                </div>
              </div>
              {p.has_receipt && <ReceiptImage paymentId={p.id} />}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
