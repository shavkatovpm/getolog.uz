"use client";

import { useEffect, useMemo, useState } from "react";
import { AdminBotRow, AdminRow, apiFetch } from "@/lib/api";
import { daysUntil, formatDate, tariffUrgency } from "@/lib/tariff";

// getolog.uz/price'dagi narxlar bilan bir xil bo'lishi shart (app/bot/keyboards.py'dagi
// TARIFF_LABELS bilan mos).
const TARIFF_OPTIONS = [
  { value: "free", label: "Bepul" },
  { value: "minimal", label: "Minimal — 295 000 so'm/oy" },
  { value: "start", label: "Standart — 590 000 so'm/oy" },
  { value: "pro", label: "Pro — 1 270 000 so'm/oy" },
  { value: "business", label: "Biznes — 1 890 000 so'm/oy" },
  { value: "scale", label: "Scale" },
];

const TONE_TEXT: Record<string, string> = {
  expired: "text-h-danger",
  urgent: "text-h-danger",
  soon: "text-h-warning",
  safe: "text-h-success",
};

function formatSom(value: number): string {
  return `${Math.round(value)
    .toString()
    .replace(/\B(?=(\d{3})+(?!\d))/g, " ")} so'm`;
}

export default function OwnerAdminsPage() {
  const [admins, setAdmins] = useState<AdminRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
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

  // Ism, @username, Telegram ID va bot/kanal nomi bo'yicha qidiriladi — owner
  // mijozni qaysi ma'lumot bilan eslasa ham topa olishi uchun.
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase().replace(/^@/, "");
    if (!q) return admins;
    return admins.filter((a) =>
      [
        a.full_name,
        a.username ?? "",
        String(a.telegram_id),
        ...a.bots.map((b) => `${b.username} ${b.channel_title ?? ""}`),
      ]
        .join(" ")
        .toLowerCase()
        .includes(q),
    );
  }, [admins, query]);

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-medium text-h-ink">
          Adminlar
          {!loading && <span className="ml-2 text-sm font-normal text-h-muted">{admins.length}</span>}
        </h1>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ism, @username, ID yoki bot bo'yicha qidirish"
          className="w-full rounded-md border border-h-border bg-h-surface px-3 py-2 text-sm text-h-ink placeholder:text-h-muted sm:w-80"
        />
      </div>

      {error && (
        <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
          {error}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-h-muted">Yuklanmoqda...</p>
      ) : admins.length === 0 ? (
        <p className="text-sm text-h-muted">Hali birorta ham admin ro&apos;yxatdan o&apos;tmagan.</p>
      ) : filtered.length === 0 ? (
        <p className="text-sm text-h-muted">Qidiruvga mos admin topilmadi.</p>
      ) : (
        <div className="space-y-4">
          {filtered.map((admin) => (
            <AdminCard
              key={admin.id}
              admin={admin}
              form={formState[admin.id] ?? { tariff: "start", months: "1" }}
              saving={savingId === admin.id}
              onFormChange={(next) => setFormState((prev) => ({ ...prev, [admin.id]: next }))}
              onSubmit={() => submitTariff(admin.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function AdminCard({
  admin,
  form,
  saving,
  onFormChange,
  onSubmit,
}: {
  admin: AdminRow;
  form: { tariff: string; months: string };
  saving: boolean;
  onFormChange: (next: { tariff: string; months: string }) => void;
  onSubmit: () => void;
}) {
  const daysLeft = admin.tariff_expiry ? daysUntil(admin.tariff_expiry) : null;
  const urgency = daysLeft === null ? "safe" : tariffUrgency(daysLeft);
  const overLimit =
    admin.subscriber_limit !== null && admin.active_subscribers > admin.subscriber_limit;

  return (
    <div className="rounded-lg border border-h-border bg-h-surface">
      {/* Sarlavha — mijozning shaxsiy ma'lumotlari va u bilan bog'lanish */}
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-h-border px-5 py-4">
        <div>
          <div className="font-medium text-h-ink">
            {admin.full_name}
            {admin.username && (
              <a
                href={`https://t.me/${admin.username}`}
                target="_blank"
                rel="noreferrer"
                className="ml-2 font-normal text-h-accent hover:underline"
              >
                @{admin.username}
              </a>
            )}
          </div>
          <div className="mt-0.5 text-xs text-h-muted">
            ID: {admin.telegram_id} · {formatDate(admin.created_at.slice(0, 10))} dan beri
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-h-ink">{admin.tariff_label}</div>
          <div className={`text-xs ${TONE_TEXT[urgency]}`}>
            {admin.tariff_expiry === null
              ? "muddat belgilanmagan"
              : daysLeft !== null && daysLeft <= 0
                ? `${formatDate(admin.tariff_expiry)} — tugagan`
                : `${formatDate(admin.tariff_expiry)} · ${daysLeft} kun qoldi`}
          </div>
        </div>
      </div>

      {/* Asosiy raqamlar */}
      <div className="grid grid-cols-2 gap-px border-b border-h-border bg-h-border sm:grid-cols-4">
        <Metric
          label="Faol obunachi"
          value={
            admin.subscriber_limit === null
              ? String(admin.active_subscribers)
              : `${admin.active_subscribers} / ${admin.subscriber_limit}`
          }
          tone={overLimit ? "text-h-danger" : undefined}
        />
        <Metric label="Umrbod obunachi" value={String(admin.lifetime_subscribers)} />
        <Metric label="Bot / kanal" value={String(admin.bots.length)} />
        <Metric label="30 kunlik tushum" value={formatSom(admin.revenue_30d)} />
      </div>

      {/* Botlar va ularning kanallari */}
      <div className="border-b border-h-border px-5 py-4">
        <div className="mb-2 text-xs font-medium tracking-wide text-h-muted uppercase">Botlari</div>
        {admin.bots.length === 0 ? (
          <p className="text-sm text-h-muted">Hali bot ulanmagan.</p>
        ) : (
          <ul className="divide-y divide-h-border rounded-md border border-h-border">
            {admin.bots.map((bot) => (
              <BotLine key={bot.id} bot={bot} />
            ))}
          </ul>
        )}
      </div>

      {/* Tarif belgilash */}
      <div className="flex flex-wrap items-center gap-2 px-5 py-4 text-sm">
        <span className="text-h-muted">Yangi tarif:</span>
        <select
          value={form.tariff}
          onChange={(e) => onFormChange({ ...form, tariff: e.target.value })}
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
          onChange={(e) => onFormChange({ ...form, months: e.target.value })}
          className="w-16 rounded-md border border-h-border bg-h-surface px-2 py-1 text-h-ink"
        />
        <span className="text-h-muted">oy</span>
        <button
          onClick={onSubmit}
          disabled={saving}
          className="rounded-md bg-h-accent px-3 py-1 text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {saving ? "..." : "Belgilash"}
        </button>
      </div>
    </div>
  );
}

function BotLine({ bot }: { bot: AdminBotRow }) {
  return (
    <li className="flex flex-wrap items-center justify-between gap-2 px-3 py-2.5 text-sm">
      <div className="min-w-0">
        <a
          href={`https://t.me/${bot.username}`}
          target="_blank"
          rel="noreferrer"
          className="font-medium text-h-accent hover:underline"
        >
          @{bot.username}
        </a>
        <div className="mt-0.5 text-xs text-h-muted">
          {bot.channel_title
            ? `${bot.channel_title} (${bot.chat_type === "group" ? "guruh" : "kanal"})`
            : "kanal ulanmagan"}
        </div>
      </div>
      <div className="flex items-center gap-4 text-xs">
        <span className="text-h-ink">{bot.active_subscribers} obunachi</span>
        <span className="text-h-muted">{formatSom(bot.revenue_30d)}</span>
        <span
          className={
            bot.permissions_ok === null
              ? "text-h-muted"
              : bot.permissions_ok
                ? "text-h-success"
                : "text-h-danger"
          }
        >
          {bot.permissions_ok === null ? "—" : bot.permissions_ok ? "Huquq OK" : "Huquq yetarli emas"}
        </span>
      </div>
    </li>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div className="bg-h-surface px-5 py-3">
      <div className="text-xs font-medium tracking-wide text-h-muted uppercase">{label}</div>
      <div className={`mt-0.5 text-base font-medium ${tone ?? "text-h-ink"}`}>{value}</div>
    </div>
  );
}
