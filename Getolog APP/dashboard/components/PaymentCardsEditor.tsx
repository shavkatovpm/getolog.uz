"use client";

import { useState } from "react";
import { Trash2, Pencil } from "lucide-react";
import {
  PaymentCardRow,
  createPaymentCard,
  deletePaymentCard,
  updatePaymentCard,
} from "@/lib/api";

interface Props {
  channelId: number;
  cards: PaymentCardRow[];
  onChanged: () => void;
}

const EMPTY_DRAFT = { bank_name: "", card_number: "", owner_name: "" };

function CardFields({
  draft,
  onChange,
}: {
  draft: typeof EMPTY_DRAFT;
  onChange: (draft: typeof EMPTY_DRAFT) => void;
}) {
  return (
    <>
      <input
        placeholder="Bank nomi (Uzcard, Humo...)"
        value={draft.bank_name}
        onChange={(e) => onChange({ ...draft, bank_name: e.target.value })}
        className="w-full rounded-md border border-h-border bg-h-surface px-2 py-1.5 text-sm text-h-ink sm:w-40"
      />
      <input
        placeholder="Karta raqami"
        value={draft.card_number}
        onChange={(e) => onChange({ ...draft, card_number: e.target.value })}
        className="w-full rounded-md border border-h-border bg-h-surface px-2 py-1.5 text-sm text-h-ink sm:w-44"
      />
      <input
        placeholder="Egasining F.I.Sh"
        value={draft.owner_name}
        onChange={(e) => onChange({ ...draft, owner_name: e.target.value })}
        className="w-full rounded-md border border-h-border bg-h-surface px-2 py-1.5 text-sm text-h-ink sm:w-44"
      />
    </>
  );
}

export function PaymentCardsEditor({ channelId, cards, onChanged }: Props) {
  const [draft, setDraft] = useState(EMPTY_DRAFT);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editDraft, setEditDraft] = useState(EMPTY_DRAFT);
  const [savingEdit, setSavingEdit] = useState(false);

  function startEdit(card: PaymentCardRow) {
    setEditingId(card.id);
    setEditDraft({
      bank_name: card.bank_name,
      card_number: card.card_number,
      owner_name: card.owner_name,
    });
  }

  async function saveEdit(cardId: number) {
    if (!editDraft.bank_name.trim() || !editDraft.card_number.trim() || !editDraft.owner_name.trim()) {
      setError("Bank nomi, karta raqami va egasining F.I.Sh to'ldirilishi shart.");
      return;
    }
    setSavingEdit(true);
    setError(null);
    try {
      await updatePaymentCard(cardId, editDraft);
      setEditingId(null);
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kartani saqlashda xatolik");
    } finally {
      setSavingEdit(false);
    }
  }

  async function addCard() {
    if (!draft.bank_name.trim() || !draft.card_number.trim() || !draft.owner_name.trim()) {
      setError("Bank nomi, karta raqami va egasining F.I.Sh to'ldirilishi shart.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await createPaymentCard(channelId, draft);
      setDraft(EMPTY_DRAFT);
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Karta qo'shishda xatolik");
    } finally {
      setSaving(false);
    }
  }

  async function removeCard(cardId: number) {
    const confirmed = window.confirm("Bu kartani o'chirmoqchimisiz?");
    if (!confirmed) return;
    setDeletingId(cardId);
    try {
      await deletePaymentCard(cardId);
      onChanged();
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div>
      {cards.length === 0 ? (
        <p className="mb-3 text-sm text-h-muted">Hali karta qo&apos;shilmagan.</p>
      ) : (
        <ul className="mb-4 divide-y divide-h-border rounded-md border border-h-border">
          {cards.map((card) =>
            editingId === card.id ? (
              <li key={card.id} className="flex flex-col gap-2 p-3 sm:flex-row sm:flex-wrap sm:items-center">
                <CardFields draft={editDraft} onChange={setEditDraft} />
                <div className="flex gap-2">
                  <button
                    onClick={() => void saveEdit(card.id)}
                    disabled={savingEdit}
                    className="rounded-md bg-h-accent px-3 py-1.5 text-sm text-white transition-opacity hover:opacity-90 disabled:opacity-50"
                  >
                    {savingEdit ? "..." : "Saqlash"}
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    className="rounded-md px-3 py-1.5 text-sm text-h-muted transition-colors hover:bg-h-bg"
                  >
                    Bekor qilish
                  </button>
                </div>
              </li>
            ) : (
              <li key={card.id} className="flex flex-col gap-2 p-3 text-sm sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="font-medium text-h-ink">{card.bank_name}</div>
                  <div className="text-h-muted">
                    {card.card_number} — {card.owner_name}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => startEdit(card)}
                    className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-h-muted transition-colors hover:bg-h-bg"
                  >
                    <Pencil size={14} />
                  </button>
                  <button
                    onClick={() => void removeCard(card.id)}
                    disabled={deletingId === card.id}
                    className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-h-danger transition-colors hover:bg-h-danger/10 disabled:opacity-40"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </li>
            )
          )}
        </ul>
      )}

      {error && (
        <p className="mb-3 rounded-md border border-h-danger/20 bg-h-danger/10 px-3 py-2 text-sm text-h-danger">
          {error}
        </p>
      )}

      <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
        <CardFields draft={draft} onChange={setDraft} />
        <button
          onClick={() => void addCard()}
          disabled={saving}
          className="rounded-md bg-h-accent px-3 py-1.5 text-sm text-white transition-opacity hover:opacity-90 disabled:opacity-50 sm:w-auto"
        >
          {saving ? "..." : "Qo'shish"}
        </button>
      </div>
    </div>
  );
}
