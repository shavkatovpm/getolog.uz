"use client";

import { useEffect, useState } from "react";
import { PlanRow, PaymentCardRow, apiFetch, listPaymentCards } from "@/lib/api";
import { useChannels } from "@/lib/channel-context";
import { PaymentCardsEditor } from "@/components/PaymentCardsEditor";
import { NumberStepper } from "@/components/NumberStepper";
import { CurrencyInput } from "@/components/CurrencyInput";
import { PageLoader } from "@/components/PageLoader";
import { useLogoGatedLoading } from "@/lib/logo-gate";

type Tab = "cards" | "plans";

const TABS: [Tab, string][] = [
  ["cards", "Kartalar"],
  ["plans", "Tarif rejalari"],
];

export default function PlansPage() {
  const { selectedChannel, loading: channelsLoading } = useChannels();
  const [tab, setTab] = useState<Tab>("plans");
  const [plans, setPlans] = useState<PlanRow[]>([]);
  const [cards, setCards] = useState<PaymentCardRow[]>([]);
  const [newPlan, setNewPlan] = useState({ duration_months: 1, price: "", is_lifetime: false });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const gatedLoading = useLogoGatedLoading(channelsLoading || loading);

  async function loadPlans(channelId: number) {
    setPlans(await apiFetch<PlanRow[]>(`/api/plans?channel_id=${channelId}`));
  }

  async function loadCards(channelId: number) {
    setCards(await listPaymentCards(channelId));
  }

  useEffect(() => {
    if (!selectedChannel) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    Promise.all([loadPlans(selectedChannel.id), loadCards(selectedChannel.id)]).finally(() =>
      setLoading(false),
    );
  }, [selectedChannel]);

  async function addPlan() {
    if (!selectedChannel) return;
    try {
      await apiFetch("/api/plans", {
        method: "POST",
        body: JSON.stringify({
          channel_id: selectedChannel.id,
          is_lifetime: newPlan.is_lifetime,
          ...(newPlan.is_lifetime ? {} : { duration_months: newPlan.duration_months }),
          price: Number(newPlan.price),
        }),
      });
      setNewPlan({ duration_months: 1, price: "", is_lifetime: false });
      await loadPlans(selectedChannel.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Tarif qo'shishda xatolik");
    }
  }

  async function addTestPlan() {
    if (!selectedChannel) return;
    try {
      await apiFetch("/api/plans", {
        method: "POST",
        body: JSON.stringify({
          channel_id: selectedChannel.id,
          duration_months: 1,
          duration_minutes: 5,
          price: 1000,
        }),
      });
      await loadPlans(selectedChannel.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Test tarif qo'shishda xatolik");
    }
  }

  async function togglePlan(plan: PlanRow) {
    if (!selectedChannel) return;
    await apiFetch(`/api/plans/${plan.id}`, {
      method: "PUT",
      body: JSON.stringify({ active: !plan.active }),
    });
    await loadPlans(selectedChannel.id);
  }

  if (gatedLoading) return <PageLoader />;
  if (!selectedChannel) return null;

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">To&apos;lov sozlamalari</h1>

      <div className="rounded-lg border border-h-border bg-h-surface">
        <div className="flex gap-1 border-b border-h-border px-3 pt-3">
          {TABS.map(([key, label]) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`rounded-t-md px-3 py-2 text-sm font-medium transition-colors ${
                tab === key
                  ? "border-x border-t border-h-border bg-h-bg text-h-ink"
                  : "text-h-muted hover:text-h-ink"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div key={tab} className="animate-card-in p-5">
          {tab === "cards" ? (
            <>
              <p className="mb-3 text-sm text-h-muted">
                Obunachi tarif tanlaganda &quot;Ushbu kartaga to&apos;lov qilib, chekni menga
                yuboring&quot; degan xabar bilan shu kartalar ko&apos;rsatiladi.
              </p>
              <PaymentCardsEditor
                channelId={selectedChannel.id}
                cards={cards}
                onChanged={() => void loadCards(selectedChannel.id)}
              />
            </>
          ) : (
            <>
              {cards.length === 0 && (
                <p className="mb-4 rounded-md border border-h-border bg-h-bg px-3 py-2 text-sm text-h-muted">
                  Diqqat: obunachilar to&apos;lov qila olishi uchun &quot;Kartalar&quot; bo&apos;limida
                  kamida bitta karta qo&apos;shishingiz kerak.
                </p>
              )}

              {error && (
                <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
                  {error}
                </p>
              )}

              <ul className="mb-4 divide-y divide-h-border rounded-md border border-h-border">
                {plans.length === 0 && (
                  <li className="p-3 text-sm text-h-muted">Hali tarif qo&apos;shilmagan</li>
                )}
                {plans.map((p) => (
                  <li key={p.id} className="flex items-center justify-between p-3 text-sm">
                    <span className="text-h-ink">
                      {p.is_lifetime
                        ? "Umrbod"
                        : p.duration_minutes != null
                          ? `${p.duration_minutes} daqiqa`
                          : `${p.duration_months} oy`}
                      {" — "}
                      {p.price.toLocaleString()} {p.currency}
                      {p.duration_minutes != null && (
                        <span className="ml-2 rounded bg-h-accent/10 px-1.5 py-0.5 text-xs text-h-accent">
                          test
                        </span>
                      )}
                    </span>
                    <button
                      onClick={() => void togglePlan(p)}
                      className={p.active ? "text-h-success" : "text-h-muted"}
                    >
                      {p.active ? "faol" : "faol emas"}
                    </button>
                  </li>
                ))}
              </ul>

              <div className="flex flex-wrap items-center gap-2">
                <label className="flex items-center gap-1.5 text-sm text-h-muted">
                  <input
                    type="checkbox"
                    checked={newPlan.is_lifetime}
                    onChange={(e) => setNewPlan((p) => ({ ...p, is_lifetime: e.target.checked }))}
                    className="rounded border-h-border"
                  />
                  Umrbod
                </label>
                {!newPlan.is_lifetime && (
                  <NumberStepper
                    value={newPlan.duration_months}
                    onChange={(n) => setNewPlan((p) => ({ ...p, duration_months: n }))}
                    min={1}
                    suffix="oy"
                  />
                )}
                <CurrencyInput
                  value={newPlan.price}
                  onChange={(v) => setNewPlan((p) => ({ ...p, price: v }))}
                  placeholder="narx"
                  className="w-40"
                />
                <button
                  onClick={() => void addPlan()}
                  className="rounded-md bg-h-accent px-3 py-1 text-sm text-white transition-opacity hover:opacity-90"
                >
                  Qo&apos;shish
                </button>
                <button
                  onClick={() => void addTestPlan()}
                  className="rounded-md border border-h-border px-3 py-1 text-sm text-h-muted transition-colors hover:bg-h-bg"
                >
                  🧪 Test tarif (5 daqiqa)
                </button>
              </div>
              <p className="mt-2 text-xs text-h-muted">
                Diqqat: umrbod reja sotib olgan obunachilar GETOLOG tarif hisobiga faqat
                birinchi 30 kun kiradi, keyin bepul hisoblanadi.
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
