/** Tarifni oshirish uchun murojaat qilinadigan jonli support akkaunt.
 * Backend'dagi nusxasi: `app/config.py:Settings.support_username` — ikkalasi bir xil bo'lsin. */
export const TARIFF_SUPPORT_URL = "https://t.me/shavkatov_ff";

const UZ_MONTHS = [
  "yanvar",
  "fevral",
  "mart",
  "aprel",
  "may",
  "iyun",
  "iyul",
  "avgust",
  "sentabr",
  "oktabr",
  "noyabr",
  "dekabr",
];

/** "YYYY-MM-DD" bilan bugungi kun orasidagi to'liq kunlar soni — vaqt zonasidan qat'iy nazar. */
export function daysUntil(isoDate: string): number {
  const [y, m, d] = isoDate.split("-").map(Number);
  const target = Date.UTC(y, m - 1, d);
  const today = new Date();
  const todayUtc = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  return Math.round((target - todayUtc) / 86_400_000);
}

export function formatDate(isoDate: string): string {
  const [y, m, d] = isoDate.split("-").map(Number);
  return `${d}-${UZ_MONTHS[m - 1]} ${y}`;
}

export type TariffUrgency = "expired" | "urgent" | "soon" | "safe";

export function tariffUrgency(daysLeft: number): TariffUrgency {
  if (daysLeft <= 0) return "expired";
  if (daysLeft <= 5) return "urgent";
  if (daysLeft <= 14) return "soon";
  return "safe";
}

export type UsageTone = "safe" | "warning" | "danger";

export interface TariffUsage {
  /** Kun bo'yicha: joriy davrning necha foizi o'tgani (0-100), aniqlanmasa null. */
  daysPercent: number | null;
  /** Obunachi bo'yicha: limitning necha foizi to'lgani (0-100), cheksiz/limitsiz bo'lsa null. */
  subscribersPercent: number | null;
  /** Ikkalasidan kattarog'i — shu asosiy ko'rsatkich sifatida ishlatiladi. */
  percent: number;
  /** Qaysi ko'rsatkich yetakchi ekanini bildiradi (UI'da tushuntirish uchun). */
  dominantMetric: "days" | "subscribers" | null;
  tone: UsageTone;
}

export function usageTone(percent: number): UsageTone {
  if (percent > 70) return "danger";
  if (percent >= 50) return "warning";
  return "safe";
}

export function computeTariffUsage(params: {
  tariffStartedAt: string | null;
  tariffExpiry: string | null;
  subscriberCount: number | null;
  subscriberLimit: number | null;
}): TariffUsage | null {
  const { tariffStartedAt, tariffExpiry, subscriberCount, subscriberLimit } = params;

  let daysPercent: number | null = null;
  if (tariffStartedAt && tariffExpiry) {
    const [sy, sm, sd] = tariffStartedAt.split("-").map(Number);
    const [ey, em, ed] = tariffExpiry.split("-").map(Number);
    const start = Date.UTC(sy, sm - 1, sd);
    const end = Date.UTC(ey, em - 1, ed);
    const today = new Date();
    const now = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
    const total = end - start;
    if (total > 0) {
      daysPercent = Math.max(0, Math.min(100, ((now - start) / total) * 100));
    }
  }

  let subscribersPercent: number | null = null;
  if (subscriberCount != null && subscriberLimit != null && subscriberLimit > 0) {
    subscribersPercent = Math.max(0, Math.min(100, (subscriberCount / subscriberLimit) * 100));
  }

  if (daysPercent === null && subscribersPercent === null) return null;

  const dominantMetric: "days" | "subscribers" | null =
    daysPercent === null
      ? "subscribers"
      : subscribersPercent === null
        ? "days"
        : daysPercent >= subscribersPercent
          ? "days"
          : "subscribers";

  const percent = Math.max(daysPercent ?? 0, subscribersPercent ?? 0);

  return { daysPercent, subscribersPercent, percent, dominantMetric, tone: usageTone(percent) };
}
