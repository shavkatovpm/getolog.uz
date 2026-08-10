"use client";

import { useState } from "react";
import { setWelcomeMessage } from "@/lib/api";

interface Props {
  channelId: number;
  initialValue: string;
  onSaved: () => void;
}

/** `key={channelId}` bilan render qilinadi — kanal almashganda komponent qayta
 * o'rnatiladi va o'sha kanalning boshlang'ich matni bilan boshlanadi. */
export function WelcomeMessageEditor({ channelId, initialValue, onSaved }: Props) {
  const [draft, setDraft] = useState(initialValue);
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await setWelcomeMessage(channelId, draft);
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
        placeholder="Masalan: Assalomu alaykum! Bu kanalda haftalik tahliliy hisobotlar beriladi."
        className="w-full rounded-md border border-h-border bg-h-surface p-2 text-sm text-h-ink"
      />
      <button
        onClick={() => void save()}
        disabled={saving}
        className="mt-2 rounded-md bg-h-accent px-3 py-1.5 text-sm text-white transition-opacity hover:opacity-90 disabled:opacity-50"
      >
        {saving ? "..." : "Saqlash"}
      </button>
    </div>
  );
}
