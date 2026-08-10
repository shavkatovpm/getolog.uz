"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { MeInfo, getMe } from "@/lib/api";

interface MeContextValue {
  me: MeInfo | null;
}

const MeContext = createContext<MeContextValue | null>(null);

/** Joriy adminning o'z tarif ma'lumotini bir marta yuklab, bo'limlar (header
 * badge, Bosh sahifa kartochkasi) o'rtasida ulashadi. */
export function MeProvider({ children }: { children: React.ReactNode }) {
  const [me, setMe] = useState<MeInfo | null>(null);

  useEffect(() => {
    getMe()
      .then(setMe)
      .catch(() => {
        /* tarif ma'lumoti ixtiyoriy — yuklanmasa badge/kartochka ko'rsatilmaydi */
      });
  }, []);

  return <MeContext.Provider value={{ me }}>{children}</MeContext.Provider>;
}

export function useMe(): MeContextValue {
  const ctx = useContext(MeContext);
  if (!ctx) throw new Error("useMe MeProvider ichida ishlatilishi kerak");
  return ctx;
}
