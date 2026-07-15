"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { ChannelRow, apiFetch } from "@/lib/api";

interface ChannelContextValue {
  channels: ChannelRow[];
  selectedChannelId: number | null;
  selectedChannel: ChannelRow | null;
  setSelectedChannelId: (id: number) => void;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

const ChannelContext = createContext<ChannelContextValue | null>(null);

/** Admin bo'limlari o'rtasida tanlangan kanalni saqlab turadi (bo'lim almashganda ham yo'qolmaydi). */
export function ChannelProvider({ children }: { children: React.ReactNode }) {
  const [channels, setChannels] = useState<ChannelRow[]>([]);
  const [selectedChannelId, setSelectedChannelId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refetch() {
    setLoading(true);
    try {
      const data = await apiFetch<ChannelRow[]>("/api/channels");
      setChannels(data);
      setSelectedChannelId((prev) => prev ?? (data.length > 0 ? data[0].id : null));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Yuklashda xatolik");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // Mount bo'lganda kanallar ro'yxatini yuklaydi.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refetch();
  }, []);

  const selectedChannel = channels.find((c) => c.id === selectedChannelId) ?? null;

  return (
    <ChannelContext.Provider
      value={{
        channels,
        selectedChannelId,
        selectedChannel,
        setSelectedChannelId,
        loading,
        error,
        refetch,
      }}
    >
      {children}
    </ChannelContext.Provider>
  );
}

export function useChannels(): ChannelContextValue {
  const ctx = useContext(ChannelContext);
  if (!ctx) throw new Error("useChannels ChannelProvider ichida ishlatilishi kerak");
  return ctx;
}
