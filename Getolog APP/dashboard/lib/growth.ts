export type GrowthWindowOption = "1m" | "3m" | "6m" | "12m" | "all";

export const GROWTH_WINDOW_LABELS: Record<GrowthWindowOption, string> = {
  "1m": "1 oy",
  "3m": "3 oy",
  "6m": "6 oy",
  "12m": "12 oy",
  all: "Doimiy",
};

const WINDOW_DAYS: Record<Exclude<GrowthWindowOption, "all">, number> = {
  "1m": 30,
  "3m": 90,
  "6m": 180,
  "12m": 365,
};

export interface GrowthPoint {
  date: string; // "YYYY-MM-DD"
  cumulative: number;
}

export interface GrowthSeries {
  windowOption: GrowthWindowOption;
  windowDays: number;
  points: GrowthPoint[];
  /** Oyna boshidagi kumulyativ son — o'sish shundan boshlab hisoblanadi. */
  startValue: number;
  /** Oyna oxiridagi (bugungi) kumulyativ son. */
  endValue: number;
}

function toUtcDay(isoDate: string): number {
  const [y, m, d] = isoDate.split("-").map(Number);
  return Date.UTC(y, m - 1, d);
}

function formatUtcDay(ms: number): string {
  const d = new Date(ms);
  const y = d.getUTCFullYear();
  const m = String(d.getUTCMonth() + 1).padStart(2, "0");
  const day = String(d.getUTCDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

function channelAgeDays(channelCreatedAt: string): number {
  const today = new Date();
  const todayUtc = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  const createdUtc = toUtcDay(channelCreatedAt);
  return Math.max(0, Math.round((todayUtc - createdUtc) / 86_400_000));
}

/** Boshlang'ich (default) oyna: kanal 3 oydan (90 kun) beri ishlatilayotgan
 * bo'lsa — 3 oy; aks holda — 1 oy. Foydalanuvchi dropdown orqali o'zgartirishi mumkin. */
export function defaultGrowthWindow(channelCreatedAt: string): GrowthWindowOption {
  return channelAgeDays(channelCreatedAt) >= 90 ? "3m" : "1m";
}

/**
 * Kanalga bot orqali qo'shilgan obunachilarning kumulyativ ("o'sib boruvchi")
 * qatorini tuzadi. Har bir obunachi faqat birinchi qo'shilgan kunida
 * hisoblanadi (backend `joined_at`ni yangilamaydi) — shuning uchun bu chiziq
 * hech qachon pasaymaydi, kanaldan chiqib ketganlar ham hisobdan olib
 * tashlanmaydi.
 */
export function buildGrowthSeries(
  channelCreatedAt: string,
  joins: string[],
  option: GrowthWindowOption
): GrowthSeries {
  const today = new Date();
  const todayUtc = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  const windowDays = option === "all" ? channelAgeDays(channelCreatedAt) || 1 : WINDOW_DAYS[option];
  const windowStartUtc = todayUtc - windowDays * 86_400_000;

  const sortedJoinDays = joins.map(toUtcDay).sort((a, b) => a - b);

  function cumulativeUpTo(dayUtc: number): number {
    let count = 0;
    for (const j of sortedJoinDays) {
      if (j <= dayUtc) count++;
      else break;
    }
    return count;
  }

  const startValue = cumulativeUpTo(windowStartUtc);
  const points: GrowthPoint[] = [];
  // Juda uzun (masalan yillik) oynada har kuni nuqta chizish shart emas —
  // ~90 tadan ko'p bo'lsa haftalik qadam bilan siyraklashtiramiz.
  const stepDays = windowDays > 120 ? 7 : 1;
  for (let day = windowStartUtc; day < todayUtc; day += stepDays * 86_400_000) {
    points.push({ date: formatUtcDay(day), cumulative: cumulativeUpTo(day) });
  }
  points.push({ date: formatUtcDay(todayUtc), cumulative: cumulativeUpTo(todayUtc) });
  const endValue = points[points.length - 1]?.cumulative ?? startValue;

  return { windowOption: option, windowDays, points, startValue, endValue };
}
