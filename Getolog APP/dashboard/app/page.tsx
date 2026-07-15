"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Send } from "lucide-react";
import { getAuth, loginWithCode, loginWithInitData, saveAuth } from "@/lib/api";
import { getTelegramWebAppInitData } from "@/lib/telegram";
import { OtpInput } from "@/components/OtpInput";

const BOT_USERNAME = process.env.NEXT_PUBLIC_BOT_USERNAME ?? "";
const BOT_LOGIN_LINK = `https://t.me/${BOT_USERNAME}?start=login`;

type Mode = "checking" | "mini-app" | "website";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("checking");
  const [code, setCode] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      loginWithInitData(initData)
        .then((auth) => {
          saveAuth(auth);
          router.replace(auth.role === "owner" ? "/owner" : "/admin");
        })
        .catch((err) => {
          setError(err instanceof Error ? err.message : "Kirishda xatolik");
        });
      return;
    }

    // Oddiy brauzer — bot orqali bir martalik kod so'raladi.
    setMode("website");
  }, [router]);

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
      <div className="flex min-h-screen items-center justify-center bg-h-bg">
        <p className="text-sm text-h-muted">Tekshirilmoqda...</p>
      </div>
    );
  }

  if (mode === "mini-app") {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-h-bg px-4 text-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-h-border border-t-h-accent" />
        <p className="text-sm text-h-muted">
          {error ?? "Telegram orqali kirilmoqda..."}
        </p>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-h-bg px-4 text-center">
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
    </div>
  );
}
