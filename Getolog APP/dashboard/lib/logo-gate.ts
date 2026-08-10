"use client";

import { useEffect, useRef, useState } from "react";

// components/LogoLoader.tsx / globals.css dagi `logo-build` animatsiyasi davri —
// 2.4s aylanadi, 50% nuqtasida (1.2s) logotip to'liq chizilgan holatda bo'ladi.
export const LOGO_CYCLE_MS = 2400;
export const LOGO_FULL_POINT_MS = LOGO_CYCLE_MS / 2;

/**
 * Ma'lumot `loading`dan tezroq tayyor bo'lsa ham, logotipni chala chizilgan
 * holatda to'xtatib qo'ymaslik uchun — qaytarilgan qiymat animatsiya
 * keyingi "to'liq chizilgan" nuqtaga yetguncha `true`da qoladi.
 */
export function useLogoGatedLoading(loading: boolean): boolean {
  const [gated, setGated] = useState(loading);
  const startRef = useRef<number | null>(null);

  useEffect(() => {
    if (loading) {
      startRef.current = Date.now();
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setGated(true);
      return;
    }
    const start = startRef.current ?? Date.now();
    const elapsed = (Date.now() - start) % LOGO_CYCLE_MS;
    const wait =
      elapsed <= LOGO_FULL_POINT_MS ? LOGO_FULL_POINT_MS - elapsed : LOGO_CYCLE_MS - elapsed + LOGO_FULL_POINT_MS;
    const timer = setTimeout(() => setGated(false), wait);
    return () => clearTimeout(timer);
  }, [loading]);

  return gated;
}
