"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Send } from "lucide-react";
import { getAuth, loginWithCode, loginWithInitData, saveAuth } from "@/lib/api";
import { getTelegramWebAppInitData } from "@/lib/telegram";
import { OtpInput } from "@/components/OtpInput";
import { LogoLoader } from "@/components/LogoLoader";

const BOT_USERNAME = process.env.NEXT_PUBLIC_BOT_USERNAME ?? "";
const BOT_LOGIN_LINK = `https://t.me/${BOT_USERNAME}?start=login`;

// Faqat `next dev`da mavjud (NODE_ENV=production'da hech qachon qurilmaydi) — lokal
// backend'da oldindan urug'langan test admin uchun tayyor token. Haqiqiy botga
// aloqasi yo'q, shuning uchun production'ga tasodifan chiqib qolsa ham xavfsiz:
// bu token production'ning JWT_SECRET_KEY'i bilan imzolanmagan.
const DEV_TEST_AUTH = {
  token:
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYWRtaW4iLCJhZG1pbl9pZCI6NCwidGVsZWdyYW1faWQiOjk5OTAwMDExMSwiZXhwIjoxNzg2OTY4MDM5fQ.vQz4LG2NqpBgYRScgnt1nB4VuSKkHhyPRqFw7nuCTlo",
  role: "admin" as const,
  admin_id: 4,
  telegram_id: 999000111,
};

// components/LogoLoader.tsx / globals.css dagi `logo-build` animatsiyasi davri —
// 2.4s aylanadi, 50% nuqtasida (1.2s) logotip to'liq chizilgan holatda bo'ladi.
const LOGO_CYCLE_MS = 2400;
const LOGO_FULL_POINT_MS = LOGO_CYCLE_MS / 2;

type Mode = "checking" | "mini-app" | "website";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("checking");
  const [code, setCode] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loaderStartRef = useRef<number | null>(null);

  useEffect(() => {
    const existing = getAuth();
    if (existing) {
      router.replace(existing.role === "owner" ? "/owner" : "/admin");
      return;
    }

    const initData = getTelegramWebAppInitData();
    if (initData) {
      // Telegram ichida (Mini App) ochilgan — kod so'ramasdan, initData orqali
      // avtomatik login qilinadi. `window.Telegram` faqat brauzerda mavjud
      // bo'lgani uchun bu holatni faqat mount bo'lgach (effect ichida)
      // aniqlash mumkin — server bilan hydration nomosligini oldini olish
      // uchun boshlang'ich holat har doim "checking" bo'lishi shart.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setMode("mini-app");
      loaderStartRef.current = Date.now();
      loginWithInitData(initData)
        .then((auth) => {
          saveAuth(auth);
          redirectWhenLogoComplete(auth.role === "owner" ? "/owner" : "/admin");
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : "Kirishda xatolik");
        });
      return;
    }

    // Oddiy brauzer — bot orqali bir martalik kod so'raladi.
    setMode("website");
  }, [router]);

  // Yangi (Telegram mini-app) kirishda — logotip animatsiyasi to'liq chizilgan
  // holatga qaytgunicha kutib, shundan keyingina sahifani almashtiradi.
  function redirectWhenLogoComplete(path: string) {
    const start = loaderStartRef.current ?? Date.now();
    const elapsed = (Date.now() - start) % LOGO_CYCLE_MS;
    const wait =
      elapsed <= LOGO_FULL_POINT_MS
        ? LOGO_FULL_POINT_MS - elapsed
        : LOGO_CYCLE_MS - elapsed + LOGO_FULL_POINT_MS;
    setTimeout(() => router.replace(path), wait);
  }

  function devLogin() {
    saveAuth(DEV_TEST_AUTH);
    router.replace("/admin");
  }

  async function submitCode(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const auth = await loginWithCode(code.trim());
      saveAuth(auth);
      router.replace(auth.role === "owner" ? "/owner" : "/admin");
    } catch {
      setError("Kod noto'g'ri yoki muddati o'tgan. Botdan yangi kod oling.");
    } finally {
      setSubmitting(false);
    }
  }

  if (mode === "checking") {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-h-bg">
        <LogoLoader size={140} />
      </div>
    );
  }

  if (mode === "mini-app") {
    return (
      <div className="flex min-h-dvh flex-col items-center justify-center gap-4 bg-h-bg px-4 text-center">
        <LogoLoader size={140} />
        <p className="text-sm text-h-muted">
          {error ?? "Telegram orqali kirilmoqda..."}
        </p>
      </div>
    );
  }

  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-6 bg-h-bg px-4 text-center">
      <div className="w-full max-w-sm rounded-xl border border-h-border bg-h-surface p-8">
        <h1 className="mb-1 text-lg font-medium tracking-tight text-h-ink">GETOLOG</h1>
        <p className="mb-6 text-sm text-h-muted">Kirish uchun Telegram orqali tasdiqlang</p>

        <div className="mb-6 text-left">
          <div className="mb-2 flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-h-accent text-xs font-medium text-white">
              1
            </span>
            <span className="text-sm font-medium text-h-ink">Botdan kod oling</span>
          </div>
          <p className="mb-2 ml-7 text-xs text-h-muted">
            Botga o&apos;ting va <code className="rounded bg-h-bg px-1 py-0.5">/parol</code>{" "}
            buyrug&apos;ini yuboring — bir martalik kod shu yerda ko&apos;rinadi.
          </p>
          <a
            href={BOT_LOGIN_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-7 inline-flex items-center gap-2 rounded-md bg-h-accent px-4 py-2 text-sm text-white transition-opacity hover:opacity-90"
          >
            <Send size={15} />
            Botga o&apos;tish
          </a>
        </div>

        <form onSubmit={submitCode} className="text-left">
          <div className="mb-2 flex items-center gap-2">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-h-accent text-xs font-medium text-white">
              2
            </span>
            <span className="text-sm font-medium text-h-ink">Kodni kiriting</span>
          </div>
          <div className="ml-7">
            <OtpInput value={code} onChange={setCode} />
            <button
              type="submit"
              disabled={submitting || code.length !== 6}
              className="mt-4 w-full rounded-md border border-h-border px-4 py-2 text-sm text-h-ink transition-colors hover:bg-h-bg disabled:opacity-40"
            >
              {submitting ? "Tekshirilmoqda..." : "Kirish"}
            </button>
          </div>
        </form>

        {error && (
          <p className="mt-5 rounded-md border border-h-danger/20 bg-h-danger/10 px-4 py-3 text-sm text-h-danger">
            {error}
          </p>
        )}
      </div>

      {process.env.NODE_ENV === "development" && (
        <button
          onClick={devLogin}
          className="text-xs text-h-muted underline decoration-dotted underline-offset-4 hover:text-h-ink"
        >
          🧪 Test admin sifatida kirish (faqat lokal)
        </button>
      )}
    </div>
  );
}
