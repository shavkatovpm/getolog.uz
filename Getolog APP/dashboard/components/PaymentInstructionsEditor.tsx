"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface Props {
  channelId: number;
  initialValue: string;
  onSaved: () => void;
}

/** `key={channelId}` bilan render qilinadi — kanal almashganda komponent qayta
 * o'rnatiladi va o'sha kanalning boshlang'ich matni bilan boshlanadi. */
export function PaymentInstructionsEditor({ channelId, initialValue, onSaved }: Props) {
  const [draft, setDraft] = useState(initialValue);
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await apiFetch(`/api/channels/${channelId}/payment-instructions`, {
        method: "PUT",
        body: JSON.stringify({ text: draft }),
      });
      onSaved();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <textarea
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        rows={3}
        placeholder="Masalan: Karta raqami 8600 **** **** 1234, F.I.O"
        className="w-full rounded border border-zinc-300 p-2"
      />
      <button
        onClick={save}
        disabled={saving}
        className="mt-2 rounded bg-zinc-900 px-3 py-1 text-sm text-white disabled:opacity-50"
      >
        {saving ? "..." : "Saqlash"}
      </button>
    </div>
  );
}
