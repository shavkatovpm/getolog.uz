"use client";

import { useChannels } from "@/lib/channel-context";
import { PaymentInstructionsEditor } from "@/components/PaymentInstructionsEditor";

export default function SettingsPage() {
  const { selectedChannel, refetch } = useChannels();
  if (!selectedChannel) return null;

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">Sozlamalar</h1>

      <div className="rounded-lg border border-h-border bg-h-surface p-5">
        <h2 className="mb-3 text-xs font-medium tracking-wide text-h-muted uppercase">
          To&apos;lov rekvizitlari
        </h2>
        <p className="mb-3 text-sm text-h-muted">
          Obunachi tarif tanlaganda shu matn (karta raqami va h.k.) ko&apos;rsatiladi.
        </p>
        <PaymentInstructionsEditor
          key={selectedChannel.id}
          channelId={selectedChannel.id}
          initialValue={selectedChannel.payment_instructions ?? ""}
          onSaved={refetch}
        />
      </div>
    </div>
  );
}
