"use client";

import { createContext, useContext, useEffect, useState } from "react";

type Theme = "light" | "dark";

interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

/** `app/layout.tsx`dagi bloklovchi inline skript sahifa render bo'lishidan oldin
 * `data-theme`ni allaqachon to'g'ri qo'ygan (miltillashni oldini olish uchun).
 * Boshlang'ich React holati serverda ham, mijozning birinchi render'ida ham
 * bir xil ("dark") bo'lishi shart — aks holda hydration nomosligi yuzaga
 * keladi. Ilova ichida (masalan Telegram WebApp skripti sabab) hydration
 * qayta tiklansa, React DOM'ni o'zi bilgan holatga qaytarib, bloklovchi
 * skript qo'ygan `data-theme` atributini yo'qotib qo'yishi mumkin — shuning
 * uchun bu effect DOM atributidan emas, doim `localStorage`dan (ishonchli
 * manba) o'qiydi va atributni har mount'da qayta tiklaydi.
 */
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("dark");

  useEffect(() => {
    const stored = localStorage.getItem("getolog_theme");
    const resolved: Theme = stored === "dark" || stored === "light" ? stored : "dark";
    setTheme(resolved);
    document.documentElement.setAttribute("data-theme", resolved);
  }, []);

  function toggleTheme() {
    setTheme((prev) => {
      const next = prev === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("getolog_theme", next);
      return next;
    });
  }

  return <ThemeContext.Provider value={{ theme, toggleTheme }}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme ThemeProvider ichida ishlatilishi kerak");
  return ctx;
}
