const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

export type Role = "owner" | "admin";

export interface AuthClaims {
  token: string;
  role: Role;
  admin_id: number | null;
  telegram_id: number;
}

export function saveAuth(auth: AuthClaims) {
  localStorage.setItem("getolog_auth", JSON.stringify(auth));
}

export function getAuth(): AuthClaims | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("getolog_auth");
  return raw ? (JSON.parse(raw) as AuthClaims) : null;
}

export function clearAuth() {
  localStorage.removeItem("getolog_auth");
}

/** Backend'ga JWT bilan so'rov yuboradi. 401 kelsa sessiyani tozalab, login sahifasiga qaytaradi. */
export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const auth = getAuth();
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (auth) headers.set("Authorization", `Bearer ${auth.token}`);

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (response.status === 401) {
    clearAuth();
    if (typeof window !== "undefined") window.location.href = "/";
    throw new Error("Sessiya tugagan, qayta kiring");
  }

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `So'rov muvaffaqiyatsiz: ${response.status}`);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

/** Chek rasmi kabi binary javoblar uchun — brauzerda ko'rsatish uchun object URL qaytaradi. */
export async function apiFetchBlobUrl(path: string): Promise<string> {
  const auth = getAuth();
  const headers = new Headers();
  if (auth) headers.set("Authorization", `Bearer ${auth.token}`);

  const response = await fetch(`${API_BASE}${path}`, { headers });
  if (!response.ok) throw new Error(`Rasmni yuklab bo'lmadi: ${response.status}`);

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

export async function loginWithCode(code: string): Promise<AuthClaims> {
  const response = await fetch(`${API_BASE}/api/auth/telegram-code`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });
  if (!response.ok) throw new Error(await response.text());
  return (await response.json()) as AuthClaims;
}

export async function loginWithInitData(initData: string): Promise<AuthClaims> {
  const response = await fetch(`${API_BASE}/api/auth/telegram-webapp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ init_data: initData }),
  });
  if (!response.ok) throw new Error(await response.text());
  return (await response.json()) as AuthClaims;
}

// ---------- Domen tiplari ----------

export interface AdminRow {
  id: number;
  telegram_id: number;
  full_name: string;
  tariff_plan: string;
  tariff_label: string;
  tariff_expiry: string | null;
  active_subscribers: number;
  lifetime_subscribers: number;
  created_at: string;
}

export interface ChannelRow {
  id: number;
  title: string;
  permissions_ok: boolean;
  payment_instructions: string | null;
  active_subscribers: number;
  monthly_revenue: number;
  admin_id: number;
  admin_full_name: string;
}

export interface SubscriberRow {
  id: number;
  user_id: number;
  status: string;
  joined_at: string;
  end_date: string;
}

export interface PlanRow {
  id: number;
  duration_months: number;
  price: number;
  currency: string;
  active: boolean;
}

export interface PaymentRow {
  id: number;
  channel_id: number;
  channel_title: string;
  admin_full_name: string;
  user_id: number;
  amount: number;
  status: string;
  created_at: string;
  has_receipt: boolean;
}

export interface ExpiringAdmin {
  id: number;
  full_name: string;
  telegram_id: number;
  tariff_label: string;
  tariff_expiry: string;
  days_left: number;
}

export interface OverviewStats {
  total_admins: number;
  total_channels: number;
  total_active_subscribers: number;
  total_revenue_30d: number;
  expiring_admins: ExpiringAdmin[];
}
