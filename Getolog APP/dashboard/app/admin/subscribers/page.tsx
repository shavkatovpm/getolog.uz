"use client";

import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { Search, Pencil, UserX, X } from "lucide-react";
import {
  SubscriberRow,
  apiFetch,
  removeSubscriber,
  updateSubscriberEndDate,
} from "@/lib/api";
import { useChannels } from "@/lib/channel-context";
import { Select } from "@/components/Select";
import { PageLoader } from "@/components/PageLoader";
import { ConfirmDialog } from "@/components/ConfirmDialog";
import { useLogoGatedLoading } from "@/lib/logo-gate";

const STATUS_LABELS: Record<string, string> = {
  active: "Faol",
  expired: "Muddati tugagan",
  removed: "Chiqarilgan",
};

const STATUS_BADGE: Record<string, string> = {
  active: "bg-h-success/10 text-h-success",
  expired: "bg-h-border text-h-muted",
  removed: "bg-h-danger/10 text-h-danger",
};

type StatusFilter = "all" | "active" | "expired" | "removed";

const FILTER_OPTIONS: [StatusFilter, string][] = [
  ["all", "Hammasi"],
  ["active", "Faol"],
  ["expired", "Muddati tugagan"],
  ["removed", "Chiqarilgan"],
];

const PAGE_SIZE = 25;

export default function SubscribersPage() {
  const { selectedChannel, loading: channelsLoading } = useChannels();
  const [subscribers, setSubscribers] = useState<SubscriberRow[]>([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const [loading, setLoading] = useState(true);
  const [editingSubscriber, setEditingSubscriber] = useState<SubscriberRow | null>(null);
  const [removingSubscriber, setRemovingSubscriber] = useState<SubscriberRow | null>(null);
  const [removing, setRemoving] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const gatedLoading = useLogoGatedLoading(channelsLoading || loading);

  async function loadSubscribers(channelId: number) {
    return apiFetch<SubscriberRow[]>(`/api/channels/${channelId}/subscribers`).then(setSubscribers);
  }

  useEffect(() => {
    if (!selectedChannel) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    loadSubscribers(selectedChannel.id).finally(() => setLoading(false));
  }, [selectedChannel]);

  async function handleRemove() {
    if (!removingSubscriber || !selectedChannel) return;
    setRemoving(true);
    try {
      await removeSubscriber(removingSubscriber.id);
      await loadSubscribers(selectedChannel.id);
      setRemovingSubscriber(null);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Chiqarishda xatolik");
    } finally {
      setRemoving(false);
    }
  }

  // Filtr yoki qidiruv o'zgarsa, "yana ko'rsatish" hisobini boshidan boshlaymiz.
  useEffect(() => {
    setVisibleCount(PAGE_SIZE);
  }, [search, statusFilter, selectedChannel]);

  const counts = useMemo(() => {
    return {
      all: subscribers.length,
      active: subscribers.filter((s) => s.status === "active").length,
      expired: subscribers.filter((s) => s.status === "expired").length,
      removed: subscribers.filter((s) => s.status === "removed").length,
    };
  }, [subscribers]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return subscribers.filter((s) => {
      if (statusFilter !== "all" && s.status !== statusFilter) return false;
      if (!q) return true;
      return (
        (s.full_name ?? "").toLowerCase().includes(q) ||
        (s.username ?? "").toLowerCase().includes(q) ||
        String(s.user_id).includes(q)
      );
    });
  }, [subscribers, search, statusFilter]);

  const visible = filtered.slice(0, visibleCount);

  if (gatedLoading) return <PageLoader />;
  if (!selectedChannel) return null;

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">Obunachilar</h1>

      {subscribers.length === 0 ? (
        <p className="text-sm text-h-muted">Hali obunachilar yo&apos;q.</p>
      ) : (
        <>
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            {/* Mobil: dropdown, joy tejash uchun */}
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
              aria-label="Holat bo'yicha filtr"
              wrapperClassName="w-full sm:hidden"
              className="w-full py-1.5 pl-2 text-sm"
            >
              {FILTER_OPTIONS.map(([key, label]) => (
                <option key={key} value={key}>
                  {label} ({counts[key]})
                </option>
              ))}
            </Select>

            {/* Desktop: tab-tugmalar */}
            <div className="hidden flex-wrap gap-1.5 sm:flex">
              {FILTER_OPTIONS.map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setStatusFilter(key)}
                  className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                    statusFilter === key
                      ? "bg-h-accent text-white"
                      : "border border-h-border text-h-muted hover:bg-h-surface"
                  }`}
                >
                  {label} ({counts[key]})
                </button>
              ))}
            </div>

            <div className="relative w-full sm:w-56">
              <Search size={14} className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-h-muted" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Ism, username yoki ID"
                className="w-full rounded-md border border-h-border bg-h-surface py-1.5 pl-8 pr-2 text-sm text-h-ink placeholder:text-h-muted"
              />
            </div>
          </div>

          {actionError && (
            <p className="mb-4 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
              {actionError}
            </p>
          )}

          {filtered.length === 0 ? (
            <p className="text-sm text-h-muted">Hech narsa topilmadi.</p>
          ) : (
            <>
              <div className="overflow-x-auto rounded-lg border border-h-border bg-h-surface">
                <table className="min-w-full text-sm">
                  <thead className="border-b border-h-border text-left">
                    <tr>
                      <th className="px-4 py-2.5 text-xs font-medium tracking-wide text-h-muted uppercase">
                        Obunachi
                      </th>
                      <th className="px-4 py-2.5 text-xs font-medium tracking-wide text-h-muted uppercase">
                        User ID
                      </th>
                      <th className="px-4 py-2.5 text-xs font-medium tracking-wide text-h-muted uppercase">
                        Holat
                      </th>
                      <th className="px-4 py-2.5 text-xs font-medium tracking-wide text-h-muted uppercase">
                        Birinchi kirgan
                      </th>
                      <th className="px-4 py-2.5 text-xs font-medium tracking-wide text-h-muted uppercase">
                        Tugash sanasi
                      </th>
                      <th className="px-4 py-2.5 text-xs font-medium tracking-wide text-h-muted uppercase">
                        Amallar
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-h-border">
                    {visible.map((s, i) => (
                      <tr key={s.id} className={i % 2 === 1 ? "bg-h-bg/40" : ""}>
                        <td className="px-4 py-2.5">
                          <div className="flex items-center gap-2.5">
                            <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-h-accent/10 text-xs font-medium text-h-accent">
                              {(s.full_name ?? s.username ?? "?")[0].toUpperCase()}
                            </span>
                            <div>
                              <div className="font-medium text-h-ink">{s.full_name ?? "—"}</div>
                              {s.username && <div className="text-xs text-h-muted">@{s.username}</div>}
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-2.5 text-h-muted">{s.user_id}</td>
                        <td className="px-4 py-2.5">
                          <span
                            className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_BADGE[s.status] ?? "bg-h-border text-h-muted"}`}
                          >
                            {STATUS_LABELS[s.status] ?? s.status}
                          </span>
                        </td>
                        <td className="px-4 py-2.5 text-h-muted">{new Date(s.joined_at).toLocaleString()}</td>
                        <td className="px-4 py-2.5 text-h-muted">
                          {s.end_date ? new Date(s.end_date).toLocaleString() : "Umrbod"}
                        </td>
                        <td className="px-4 py-2.5">
                          {s.status === "active" && (
                            <div className="flex items-center gap-1">
                              <button
                                type="button"
                                aria-label="Muddatni o'zgartirish"
                                onClick={() => setEditingSubscriber(s)}
                                className="flex h-7 w-7 items-center justify-center rounded-md text-h-muted transition-colors hover:bg-h-bg hover:text-h-ink"
                              >
                                <Pencil size={14} />
                              </button>
                              <button
                                type="button"
                                aria-label="Chiqarish"
                                onClick={() => setRemovingSubscriber(s)}
                                className="flex h-7 w-7 items-center justify-center rounded-md text-h-muted transition-colors hover:bg-h-danger/10 hover:text-h-danger"
                              >
                                <UserX size={14} />
                              </button>
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-3 flex items-center justify-between text-xs text-h-muted">
                <span>
                  {visible.length} / {filtered.length} ko&apos;rsatilmoqda
                </span>
                {visibleCount < filtered.length && (
                  <button
                    onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}
                    className="rounded-md border border-h-border px-3 py-1.5 font-medium text-h-ink transition-colors hover:bg-h-surface"
                  >
                    Yana {Math.min(PAGE_SIZE, filtered.length - visibleCount)} ta ko&apos;rsatish
                  </button>
                )}
              </div>
            </>
          )}
        </>
      )}

      {editingSubscriber && selectedChannel && (
        <EditEndDateModal
          subscriber={editingSubscriber}
          onClose={() => setEditingSubscriber(null)}
          onSaved={() => {
            setEditingSubscriber(null);
            void loadSubscribers(selectedChannel.id);
          }}
        />
      )}

      <ConfirmDialog
        open={!!removingSubscriber}
        title="Obunachini chiqarish"
        message={
          removingSubscriber
            ? `${removingSubscriber.full_name ?? removingSubscriber.username ?? removingSubscriber.user_id} rostdan ham chiqarilsinmi? U darhol kanal/guruhdan chiqariladi.`
            : ""
        }
        confirmLabel="Ha, chiqarish"
        confirming={removing}
        onConfirm={() => void handleRemove()}
        onCancel={() => setRemovingSubscriber(null)}
      />
    </div>
  );
}

function EditEndDateModal({
  subscriber,
  onClose,
  onSaved,
}: {
  subscriber: SubscriberRow;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [isLifetime, setIsLifetime] = useState(subscriber.end_date === null);
  const [value, setValue] = useState(() =>
    subscriber.end_date ? subscriber.end_date.slice(0, 16) : "",
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [onClose]);

  async function save() {
    if (!isLifetime && !value) {
      setError("Sanani tanlang yoki 'Umrbod' belgilang");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await updateSubscriberEndDate(subscriber.id, isLifetime ? null : new Date(value).toISOString());
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Saqlashda xatolik");
    } finally {
      setSaving(false);
    }
  }

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={(e) => e.stopPropagation()}
    >
      <button
        type="button"
        aria-label="Yopish"
        onClick={onClose}
        className="animate-modal-backdrop absolute inset-0 bg-black/50"
      />
      <div className="animate-modal-panel relative w-full max-w-sm rounded-lg border border-h-border bg-h-surface p-5 shadow-xl">
        <button
          type="button"
          aria-label="Yopish"
          onClick={onClose}
          className="absolute top-3 right-3 flex h-7 w-7 items-center justify-center rounded-md text-h-muted transition-colors hover:bg-h-bg hover:text-h-ink"
        >
          <X size={16} />
        </button>
        <h2 className="mb-1 pr-6 text-sm font-medium text-h-ink">Muddatni o&apos;zgartirish</h2>
        <p className="mb-4 text-xs text-h-muted">
          {subscriber.full_name ?? subscriber.username ?? subscriber.user_id}
        </p>

        <label className="mb-3 flex items-center gap-1.5 text-sm text-h-ink">
          <input
            type="checkbox"
            checked={isLifetime}
            onChange={(e) => setIsLifetime(e.target.checked)}
            className="rounded border-h-border"
          />
          Umrbod (muddatsiz)
        </label>

        {!isLifetime && (
          <input
            type="datetime-local"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            className="mb-3 w-full rounded-md border border-h-border bg-h-surface px-2 py-1.5 text-sm text-h-ink"
          />
        )}

        {error && <p className="mb-3 text-xs text-h-danger">{error}</p>}

        <button
          type="button"
          onClick={() => void save()}
          disabled={saving}
          className="w-full rounded-md bg-h-accent px-3 py-2 text-sm text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {saving ? "..." : "Saqlash"}
        </button>
      </div>
    </div>,
    document.body,
  );
}
