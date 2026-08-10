"use client";

import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";
import { useChannels } from "@/lib/channel-context";
import { BotRow, deleteBot, listBots } from "@/lib/api";
import { WelcomeMessageEditor } from "@/components/WelcomeMessageEditor";
import { ConfirmDialog } from "@/components/ConfirmDialog";

export default function SettingsPage() {
  const { selectedChannel, refetch: refetchChannels } = useChannels();
  const [bots, setBots] = useState<BotRow[]>([]);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    void listBots().then(setBots);
  }, [selectedChannel]);

  const currentBot = selectedChannel ? bots.find((b) => b.channel_id === selectedChannel.id) : undefined;
  const kind = selectedChannel?.chat_type === "group" ? "guruh" : "kanal";

  async function handleDelete() {
    if (!currentBot) return;
    setDeleting(true);
    try {
      await deleteBot(currentBot.id);
      await Promise.all([listBots().then(setBots), refetchChannels()]);
      setConfirmOpen(false);
    } catch (err) {
      alert(err instanceof Error ? err.message : "O'chirishda xatolik");
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-lg font-medium text-h-ink">Sozlamalar</h1>

      {selectedChannel && (
        <div className="mb-6 rounded-lg border border-h-border bg-h-surface p-5">
          <h2 className="mb-3 text-xs font-medium tracking-wide text-h-muted uppercase">
            Xush kelibsiz xabari
          </h2>
          <p className="mb-3 text-sm text-h-muted">
            Obunachi shaxsiy botga /start bosganda, tarif tanlashdan oldin shu matn
            ko&apos;rsatiladi (masalan {kind} haqida qisqa ma&apos;lumot). Bo&apos;sh
            qoldirilsa, hech qanday qo&apos;shimcha matn chiqmaydi.
          </p>
          <WelcomeMessageEditor
            key={selectedChannel.id}
            channelId={selectedChannel.id}
            initialValue={selectedChannel.welcome_message ?? ""}
            onSaved={refetchChannels}
          />
        </div>
      )}

      {currentBot && (
        <div className="rounded-lg border border-h-danger/25 bg-h-danger/5 p-5">
          <h2 className="mb-3 text-xs font-medium tracking-wide text-h-danger uppercase">
            Botni o&apos;chirish
          </h2>
          <p className="mb-3 text-sm text-h-muted">
            @{currentBot.username} — hozir tanlangan {kind}ga ({selectedChannel?.title}) ulangan bot.
            Boshqa botni o&apos;chirish uchun avval navbardagi tanlovdan o&apos;sha {kind}ga
            o&apos;ting.
          </p>
          <button
            onClick={() => setConfirmOpen(true)}
            className="flex items-center gap-1.5 rounded-md bg-h-danger px-3 py-1.5 text-sm text-white transition-opacity hover:opacity-90"
          >
            <Trash2 size={14} />
            Botni o&apos;chirish
          </button>
        </div>
      )}

      <ConfirmDialog
        open={confirmOpen}
        title="Botni o'chirish"
        message={
          currentBot
            ? `@${currentBot.username} botini rostdan ham o'chirmoqchimisiz? Bu amalni ortga qaytarib bo'lmaydi — ${kind}, obunachilar va tarif ma'lumotlari ham o'chadi.`
            : ""
        }
        confirmLabel="Ha, o'chirish"
        confirming={deleting}
        onConfirm={() => void handleDelete()}
        onCancel={() => setConfirmOpen(false)}
      />
    </div>
  );
}
