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

export type ChatType = "channel" | "group";

/** Admin ulagan bitta bot va uning kanali (owner panelidagi admin qatori ichida). */
export interface AdminBotRow {
  id: number;
  username: string;
  channel_id: number | null;
  channel_title: string | null;
  chat_type: ChatType | null;
  permissions_ok: boolean | null;
  active_subscribers: number;
  revenue_30d: number;
}

export interface AdminRow {
  id: number;
  telegram_id: number;
  full_name: string;
  username: string | null;
  tariff_plan: string;
  tariff_label: string;
  tariff_expiry: string | null;
  tariff_started_at: string | null;
  subscriber_limit: number | null;
  limit_exceeded_at: string | null;
  active_subscribers: number;
  lifetime_subscribers: number;
  revenue_30d: number;
  bots: AdminBotRow[];
  created_at: string;
}

export interface ChannelRow {
  id: number;
  title: string;
  chat_type: ChatType;
  permissions_ok: boolean;
  welcome_message: string | null;
  active_subscribers: number;
  monthly_revenue: number;
  bot_username: string;
  admin_id: number;
  admin_full_name: string;
  admin_username: string | null;
  admin_telegram_id: number;
}

export interface ChannelGrowth {
  channel_created_at: string;
  joins: string[];
}

export async function getChannelGrowth(channelId: number): Promise<ChannelGrowth> {
  return apiFetch<ChannelGrowth>(`/api/channels/${channelId}/growth`);
}

export async function setWelcomeMessage(channelId: number, text: string): Promise<void> {
  await apiFetch<void>(`/api/channels/${channelId}/welcome-message`, {
    method: "PUT",
    body: JSON.stringify({ text }),
  });
}

export interface PaymentCardRow {
  id: number;
  bank_name: string;
  card_number: string;
  owner_name: string;
}

export async function listPaymentCards(channelId: number): Promise<PaymentCardRow[]> {
  return apiFetch<PaymentCardRow[]>(`/api/channels/${channelId}/payment-cards`);
}

export async function createPaymentCard(
  channelId: number,
  card: { bank_name: string; card_number: string; owner_name: string }
): Promise<PaymentCardRow> {
  return apiFetch<PaymentCardRow>(`/api/channels/${channelId}/payment-cards`, {
    method: "POST",
    body: JSON.stringify(card),
  });
}

export async function updatePaymentCard(
  cardId: number,
  card: { bank_name: string; card_number: string; owner_name: string }
): Promise<PaymentCardRow> {
  return apiFetch<PaymentCardRow>(`/api/payment-cards/${cardId}`, {
    method: "PUT",
    body: JSON.stringify(card),
  });
}

export async function deletePaymentCard(cardId: number): Promise<void> {
  await apiFetch<void>(`/api/payment-cards/${cardId}`, { method: "DELETE" });
}

export interface SubscriberRow {
  id: number;
  user_id: number;
  username: string | null;
  full_name: string | null;
  status: string;
  joined_at: string;
  end_date: string | null;
}

/** `endDate: null` — obunachini umrbod (muddatsiz) qiladi. */
export async function updateSubscriberEndDate(
  subscriberId: number,
  endDate: string | null,
): Promise<{ id: number; end_date: string | null }> {
  return apiFetch(`/api/subscribers/${subscriberId}`, {
    method: "PUT",
    body: JSON.stringify({ end_date: endDate }),
  });
}

export async function removeSubscriber(subscriberId: number): Promise<{ id: number; status: string }> {
  return apiFetch(`/api/subscribers/${subscriberId}/remove`, { method: "POST" });
}

export interface PlanRow {
  id: number;
  duration_months: number | null;
  duration_minutes: number | null;
  is_lifetime: boolean;
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
  subscriber_username: string | null;
  subscriber_full_name: string | null;
  amount: number;
  status: string;
  created_at: string;
  has_receipt: boolean;
}

export interface BotRow {
  id: number;
  username: string;
  channel_id: number | null;
  channel_title: string | null;
  chat_type: ChatType | null;
  permissions_ok: boolean | null;
}

export async function listBots(): Promise<BotRow[]> {
  return apiFetch<BotRow[]>("/api/bots");
}

export async function deleteBot(botId: number): Promise<void> {
  await apiFetch<void>(`/api/bots/${botId}`, { method: "DELETE" });
}

export interface MeInfo {
  tariff_plan: string | null;
  tariff_label: string | null;
  tariff_expiry: string | null;
  tariff_started_at: string | null;
  subscriber_count: number | null;
  subscriber_limit: number | null;
  limit_exceeded_at: string | null;
}

export async function getMe(): Promise<MeInfo> {
  return apiFetch<MeInfo>("/api/me");
}

export interface ExpiringAdmin {
  id: number;
  full_name: string;
  username: string | null;
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
