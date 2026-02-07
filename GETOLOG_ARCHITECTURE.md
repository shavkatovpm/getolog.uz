# GETOLOG — System Architecture Document (v2.0 — Tasdiqlangan)

## 1. Loyiha haqida umumiy ma'lumot

**GETOLOG** — Telegram bot orqali pullik kanal/guruhga kirish (paid access) tizimini avtomatik generatsiya qiluvchi SaaS platforma.

**Asosiy g'oya:** Har qanday odam o'z Telegram bot tokenini GETOLOG'ga yuboradi va GETOLOG shu token orqali avtomatlashtirilgan "sotuvchi bot" yaratib beradi. End userlar shu bot orqali to'lov qilib, yopiq kanal/guruhga bir martalik invite link oladi.

---

## 2. Foydalanuvchi rollari

```
┌─────────────────────────────────────────────────────┐
│                    MODERATOR                         │
│            (Getolog platformasi admini)              │
│         Butun tizimni boshqaradi                     │
├─────────────────────────────────────────────────────┤
│                   USER ADMIN                         │
│             (Kanal/guruh egasi)                      │
│    O'z bot tokenini beradi, sotuvchi bot oladi       │
├─────────────────────────────────────────────────────┤
│                    END USER                          │
│              (Oddiy foydalanuvchi)                   │
│   User Admin botiga kirib to'lov qiladi,            │
│   yopiq kanal/guruhga link oladi                    │
└─────────────────────────────────────────────────────┘
```

### 2.1 Moderator (Platformani boshqaruvchi)
- Barcha User Admin'larni ko'rish, ban qilish
- Barcha to'lovlarni kuzatish
- User Admin obunalarini qo'lda berish/uzaytirish
- Umumiy statistika
- Bildirishnomalar: yangi User Admin ro'yxatdan o'tdi, obuna tugadi

### 2.2 User Admin (Kanal egasi)
- Bot tokenini yuboradi → avtomatlashtirilgan bot oladi
- 1 ta bot = 1 ta kanal link + 1 ta guruh link qo'shish mumkin
- Sozlamalar: narxlar, to'lov usuli, bot xabarlari (default mavjud)
- Kanal muddat belgilash: 1 oy / 6 oy / 12 oy / umrbod
- Statistika: to'lovlar soni, tushum, end userlar
- End userlarni boshqarish: ban, qo'lda link berish
- To'lovlarni tasdiqlash (manual to'lov uchun)
- Bildirishnomalar: yangi to'lov, yangi end user, obuna tugash ogohlantirishlari

### 2.3 End User (Oxirgi foydalanuvchi)
- Bot'ga /start bosadi
- Til tanlaydi (UZ/EN/RU)
- Narxlarni ko'radi
- To'lov usulini tanlaydi
- To'lov qiladi → bir martalik invite link oladi
- Support orqali admin bilan gaplashishi mumkin
- Bildirishnomalar: muddat tugashiga 3 kun/1 kun qoldi, kanaldan chiqarildi

---

## 3. Biznes modeli

### 3.1 Monetizatsiya
```
GETOLOG daromad manbalari:
├── User Admin obunalari (asosiy daromad)
│   ├── Bepul tarif — reklama bilan (start sahifasida, til tanlashda)
│   ├── 1 oylik obuna
│   ├── 6 oylik obuna
│   └── 12 oylik obuna
│
└── Bir martalik xizmatlar
    └── Click/Payme/Uzum integratsiyasi (qo'lda ulab berish)
```

### 3.2 Bepul tarif
- To'liq funksionallik
- End User /start bosganda til tanlash qismida GETOLOG reklamasi ko'rinadi
- Faqat karta (manual) to'lov usuli mavjud

### 3.3 Pullik tariflar (1/6/12 oy)
- Reklama yo'q
- Karta (manual) to'lov — default
- Click/Payme/Uzum integratsiyasi — qo'shimcha bir martalik to'lov evaziga

### 3.4 Obuna tugash logikasi
- 3 kun oldin → ogohlantirish
- 1 kun oldin → ogohlantirish
- Muddat tugadi → avtomatik bepul tarifga o'tish (reklama paydo bo'ladi)

---

## 4. End User to'lov flow'lari

### 4.1 Karta (Manual) to'lov — barcha tariflar uchun
```
End User                    Bot                     User Admin
   │                         │                          │
   ├── /start ──────────────►│                          │
   │◄── Til tanlash ─────────┤                          │
   ├── Tilni tanladi ───────►│                          │
   │◄── Narxlar + to'lov ────┤                          │
   │    usulini ko'rsatadi    │                          │
   ├── "Karta orqali" ──────►│                          │
   │◄── Admin karta raqamini  │                          │
   │    ko'rsatadi            │                          │
   ├── Pul o'tkazadi ────────────────────────────────────┤
   ├── Screenshot/chek ─────►│                          │
   │                         ├── Yangi to'lov! ────────►│
   │                         │◄── Tasdiqladi ───────────┤
   │◄── Invite link ─────────┤                          │
   │    (bir martalik)        │                          │
```

### 4.2 Click/Payme/Uzum — pullik xizmat orqali ulangan (MVP'dan keyin)
```
End User                    Bot                     To'lov tizimi
   │                         │                          │
   ├── "Click orqali" ──────►│                          │
   │◄── To'lov havolasi ─────┤                          │
   ├── To'lov qiladi ───────────────────────────────────►│
   │                         │◄── Callback (muvaffaqiyat)│
   │◄── Invite link ─────────┤                          │
   │    (bir martalik)        │                          │
```

To'lov to'g'ridan-to'g'ri User Admin kartasiga tushadi.

---

## 5. Texnik arxitektura

### 5.1 Tech Stack

| Komponent | Texnologiya | Sabab |
|-----------|-------------|-------|
| Dasturlash tili | Python 3.11+ | Telegram bot ekosistemasi kuchli |
| Bot framework | aiogram 3 | Async, multi-bot qo'llab-quvvatlash |
| Web framework | aiohttp | Webhook server uchun (aiogram ichida mavjud) |
| Database | PostgreSQL | Relatsion ma'lumotlar, Neon/Supabase free tier |
| Cache / FSM / Queue | Redis | FSM state, token cache, rate limiting, task queue |
| ORM | SQLAlchemy + Alembic | Migration'lar, type safety |
| Scheduler | APScheduler | Cron vazifalar (Redis lock bilan) |
| Monitoring | Sentry (free tier) | Error tracking va alertlar |
| Shifrlash | Fernet (cryptography) | Bot token himoyasi |
| Hosting | DigitalOcean | $6/oy droplet, barqaror |

### 5.2 Arxitektura diagrammasi

```
┌───────────────────────────────────────────────────────┐
│              DigitalOcean Droplet ($6/oy)              │
│              Ubuntu 22.04, 1GB RAM, 1 vCPU            │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │            GETOLOG Main Process                 │  │
│  │                                                 │  │
│  │  ┌──────────────────┐  ┌─────────────────────┐  │  │
│  │  │  aiohttp Server  │  │   Main Bot          │  │  │
│  │  │  (Webhook qabul) │  │   (Getolog)         │  │  │
│  │  │                  │  │                     │  │  │
│  │  │  POST /webhook/  │  │  - Ro'yxatdan o'tish│  │  │
│  │  │  {bot_token}     │  │  - Token qabul      │  │  │
│  │  │  ───────────────►│  │  - Sozlamalar       │  │  │
│  │  │                  │  │  - Moderator panel  │  │  │
│  │  └──────────────────┘  └─────────────────────┘  │  │
│  │                                                 │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │           Bot Manager Service            │   │  │
│  │  │                                          │   │  │
│  │  │  - Webhook ro'yxatdan o'tkazish          │   │  │
│  │  │  - Bot lifecycle (start/stop/restart)    │   │  │
│  │  │  - Token validatsiya (getMe)             │   │  │
│  │  │  - Graceful error handling               │   │  │
│  │  │  - Health check (bot alive/dead)         │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                 │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │          Scheduler Service               │   │  │
│  │  │          (APScheduler + Redis lock)       │   │  │
│  │  │                                          │   │  │
│  │  │  ⏰ Har 10 daqiqada:                      │   │  │
│  │  │  ├── End user kanaldan chiqarish         │   │  │
│  │  │  └── Admin obuna tugatish               │   │  │
│  │  │                                          │   │  │
│  │  │  ⏰ Har 6 soatda:                         │   │  │
│  │  │  ├── Ogohlantirish (3 kun / 1 kun)       │   │  │
│  │  │  └── Bot health check                   │   │  │
│  │  │                                          │   │  │
│  │  │  ⏰ Server start:                         │   │  │
│  │  │  └── Barcha aktiv botlar webhook qayta   │   │  │
│  │  │      ro'yxatdan o'tkazish                │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────┘  │
│                        │                              │
│            ┌───────────┼───────────┐                  │
│            ▼           ▼           ▼                  │
│  ┌──────────────┐ ┌─────────┐ ┌─────────┐            │
│  │  PostgreSQL  │ │  Redis  │ │ Sentry  │            │
│  │  (Neon Free) │ │ (local) │ │ (free)  │            │
│  │              │ │  ~50MB  │ │ (cloud) │            │
│  │  - Models    │ │         │ │         │            │
│  │  - Payments  │ │ - FSM   │ │ - Error │            │
│  │  - Users     │ │ - Cache │ │   track │            │
│  └──────────────┘ │ - Lock  │ │ - Alert │            │
│                   └─────────┘ └─────────┘            │
└───────────────────────────────────────────────────────┘
```

### 5.3 Polling vs Webhook — nima uchun Webhook?

```
POLLING (eski reja):                    WEBHOOK (yangi reja):
─────────────────────                   ──────────────────────
100 bot = 100 TCP ulanish              100 bot = 1 HTTP server
~600MB RAM                             ~150MB RAM
Har bot alohida so'rov yuboradi        Telegram o'zi so'rov yuboradi
Server yuklanishi yuqori               Server yuklanishi past
Scale qilish qiyin                     Scale qilish oson
```

### 5.4 Multi-Bot boshqaruv tizimi (Webhook asosida)

```python
# Konseptual arxitektura
class BotManager:
    """Barcha User Admin botlarini webhook orqali boshqaradi"""

    bots: dict[int, Bot]          # user_admin_id -> Bot instance
    dispatchers: dict[int, Dispatcher]  # user_admin_id -> Dispatcher

    async def register_bot(self, token: str, user_admin_id: int) -> bool:
        """Yangi bot qo'shish — token validatsiya + webhook o'rnatish"""
        # 1. Token validatsiya
        bot = Bot(token=token)
        try:
            bot_info = await bot.get_me()  # Token haqiqiymi?
        except TelegramAPIError:
            return False  # Noto'g'ri token

        # 2. Dispatcher yaratish
        dp = Dispatcher(storage=RedisStorage.from_url(REDIS_URL))
        dp.include_router(end_user_router)

        # 3. Webhook o'rnatish
        webhook_url = f"{SERVER_URL}/webhook/{token}"
        await bot.set_webhook(webhook_url)

        # 4. Saqlash
        self.bots[user_admin_id] = bot
        self.dispatchers[user_admin_id] = dp
        return True

    async def handle_update(self, token: str, update: dict):
        """Telegram'dan kelgan update'ni tegishli botga yo'naltirish"""
        user_admin_id = self._find_by_token(token)
        bot = self.bots[user_admin_id]
        dp = self.dispatchers[user_admin_id]
        try:
            await dp.feed_update(bot, Update(**update))
        except Exception as e:
            # Bitta bot xatosi boshqalarga ta'sir qilmaydi
            sentry_sdk.capture_exception(e)
            logger.error(f"Bot {user_admin_id} xatosi: {e}")

    async def stop_bot(self, user_admin_id: int):
        """Botni to'xtatish va webhook o'chirish"""
        bot = self.bots.pop(user_admin_id, None)
        if bot:
            await bot.delete_webhook()
            await bot.session.close()
        self.dispatchers.pop(user_admin_id, None)

    async def health_check(self) -> dict:
        """Barcha botlar holatini tekshirish"""
        results = {}
        for uid, bot in self.bots.items():
            try:
                await bot.get_me()
                results[uid] = "alive"
            except Exception:
                results[uid] = "dead"
                # Auto-restart o'rnatish mumkin
        return results
```

### 5.5 Webhook Server (aiohttp)

```python
# main.py — webhook qabul qiluvchi server
from aiohttp import web

app = web.Application()
bot_manager = BotManager()

async def webhook_handler(request: web.Request):
    """Barcha botlar uchun yagona webhook endpoint"""
    token = request.match_info["token"]
    update = await request.json()
    await bot_manager.handle_update(token, update)
    return web.Response(status=200)

app.router.add_post("/webhook/{token}", webhook_handler)

# Server ishga tushadi — port 8443 yoki nginx orqali proxy
web.run_app(app, host="0.0.0.0", port=8443)
```

---

## 6. Database Schema (Tuzatilgan)

### 6.1 ER Diagramma

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   user_admins    │     │    user_bots     │     │    channels      │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ id (PK)          │────►│ id (PK)          │────►│ id (PK)          │
│ telegram_id (UQ) │     │ user_admin_id(FK)│     │ user_bot_id (FK) │
│ username         │     │ bot_token (enc)  │     │ telegram_chat_id │
│ full_name        │     │ bot_username     │     │ type (channel/   │
│ language         │     │ is_active        │     │       group)     │
│ banned           │     │ welcome_message  │     │ title            │
│ created_at       │     │ payment_method   │     │ price            │
└──────────────────┘     │ card_number      │     │ currency (UZS)   │
                         │ created_at       │     │ duration_months  │
                         └──────────────────┘     │ (1/6/12/0=umrbod)│
                                  │               └──────────────────┘
                                  │
                         ┌──────────────────┐     ┌──────────────────┐
                         │    end_users     │     │    payments      │
                         ├──────────────────┤     ├──────────────────┤
                         │ id (PK)          │     │ id (PK)          │
                         │ telegram_id      │     │ end_user_id (FK) │
                         │ user_bot_id (FK) │     │ user_bot_id (FK) │
                         │ username         │     │ channel_id (FK)  │
                         │ language         │     │ amount           │
                         │ banned           │     │ payment_method   │
                         │ created_at       │     │ status (pending/ │
                         │                  │     │  approved/       │
                         │ UNIQUE(          │     │  rejected)       │
                         │  telegram_id,    │     │ screenshot_file  │
                         │  user_bot_id)    │     │ created_at       │
                         └──────────────────┘     │ approved_at      │
                                                  └──────────────────┘
                         ┌──────────────────┐
                         │  subscriptions   │
                         ├──────────────────┤
                         │ id (PK)          │
                         │ end_user_id (FK) │
                         │ channel_id (FK)  │
                         │ payment_id (FK)  │
                         │ invite_link      │
                         │ link_used (bool) │
                         │ joined_at        │
                         │ expires_at       │
                         │ kicked_at        │
                         │ status (active/  │
                         │  expired/kicked) │
                         │ notified_3day    │
                         │ notified_1day    │
                         └──────────────────┘

                         ┌──────────────────┐
                         │admin_subscriptions│
                         ├──────────────────┤
                         │ id (PK)          │
                         │ user_admin_id(FK)│
                         │ plan (free/1m/   │
                         │   6m/12m)        │
                         │ started_at       │
                         │ expires_at       │
                         │ amount_paid      │
                         │ status (active/  │
                         │   expired)       │
                         │ notified_3day    │
                         │ notified_1day    │
                         └──────────────────┘
```

### 6.2 Eski versiyadan farqlari

| O'zgarish | Sabab |
|-----------|-------|
| `notifications` jadvali **olib tashlandi** | Telegram o'zi xabar yetkazganini tasdiqlaydi, alohida jadval ortiqcha |
| `user_bots` dan `subscription_type`, `subscription_end` **olib tashlandi** | `admin_subscriptions` jadvalida bor — duplikatsiya edi |
| `end_users` ga `UNIQUE(telegram_id, user_bot_id)` **qo'shildi** | Bitta odam bitta botda bir marta ro'yxatdan o'tishi kerak |
| `subscriptions.expires_at` ga **INDEX qo'shildi** | Scheduler tez qidirishi uchun |
| `payments.status` ga **INDEX qo'shildi** | Pending to'lovlarni tez topish uchun |
| `end_users.telegram_id` ga **INDEX qo'shildi** | Foydalanuvchini tez aniqlash uchun |

### 6.3 Jadvallar tafsiloti

#### user_admins
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | SERIAL PK | Ichki ID |
| telegram_id | BIGINT UNIQUE | Telegram user ID |
| username | VARCHAR(255) | Telegram username |
| full_name | VARCHAR(255) | Telegram ism |
| language | VARCHAR(5) | Tanlangan til (uz/en/ru) |
| banned | BOOLEAN DEFAULT FALSE | Ban holati |
| created_at | TIMESTAMP DEFAULT NOW | Ro'yxatdan o'tgan vaqt |

#### user_bots
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | SERIAL PK | Ichki ID |
| user_admin_id | FK → user_admins | Bot egasi |
| bot_token | TEXT (encrypted) | Bot tokeni (Fernet bilan shifrlangan) |
| bot_username | VARCHAR(255) | Bot username (@nomi) |
| is_active | BOOLEAN DEFAULT TRUE | Bot ishlayaptimi |
| welcome_message | TEXT | Salomlash xabari (default mavjud) |
| payment_method | VARCHAR(50) DEFAULT 'card' | card / click / payme / uzum |
| card_number | VARCHAR(20) | Admin karta raqami (manual uchun) |
| created_at | TIMESTAMP DEFAULT NOW | Yaratilgan vaqt |

#### channels
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | SERIAL PK | Ichki ID |
| user_bot_id | FK → user_bots | Qaysi botga tegishli |
| telegram_chat_id | BIGINT | Telegram kanal/guruh ID |
| type | ENUM('channel','group') | Kanal yoki guruh |
| title | VARCHAR(255) | Kanal/guruh nomi |
| price | DECIMAL(12,2) | Kirish narxi (UZS katta sonlar uchun 12 xona) |
| currency | VARCHAR(10) DEFAULT 'UZS' | Valyuta |
| duration_months | INTEGER | 1/6/12/0 (0=umrbod) |

#### end_users
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | SERIAL PK | Ichki ID |
| telegram_id | BIGINT | Telegram user ID |
| user_bot_id | FK → user_bots | Qaysi bot orqali kirgan |
| username | VARCHAR(255) | Telegram username |
| language | VARCHAR(5) | Tanlangan til |
| banned | BOOLEAN DEFAULT FALSE | Ban holati |
| created_at | TIMESTAMP DEFAULT NOW | Birinchi kirgan vaqt |
| | **UNIQUE(telegram_id, user_bot_id)** | Bir odam — bir bot |

#### payments
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | SERIAL PK | Ichki ID |
| end_user_id | FK → end_users | Kim to'ladi |
| user_bot_id | FK → user_bots | Qaysi bot uchun |
| channel_id | FK → channels | Qaysi kanal uchun |
| amount | DECIMAL(12,2) | To'lov summasi |
| payment_method | VARCHAR(50) | card/click/payme/uzum |
| status | ENUM('pending','approved','rejected') | To'lov holati |
| screenshot_file_id | TEXT | Telegram file ID (chek rasmi) |
| created_at | TIMESTAMP DEFAULT NOW | To'lov vaqti |
| approved_at | TIMESTAMP NULL | Tasdiqlangan vaqt |
| | **INDEX(status)** | Tez qidiruv uchun |

#### subscriptions
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | SERIAL PK | Ichki ID |
| end_user_id | FK → end_users | Obunachi |
| channel_id | FK → channels | Kanal |
| payment_id | FK → payments | Tegishli to'lov |
| invite_link | TEXT | Bir martalik invite link |
| link_used | BOOLEAN DEFAULT FALSE | Link ishlatildimi |
| joined_at | TIMESTAMP NULL | Kanalga qo'shilgan vaqt |
| expires_at | TIMESTAMP NULL | Muddat tugash vaqti (NULL=umrbod) |
| kicked_at | TIMESTAMP NULL | Chiqarilgan vaqt |
| status | ENUM('active','expired','kicked') | Obuna holati |
| notified_3day | BOOLEAN DEFAULT FALSE | 3 kun ogohlantirish |
| notified_1day | BOOLEAN DEFAULT FALSE | 1 kun ogohlantirish |
| | **INDEX(expires_at, status)** | Scheduler uchun |

#### admin_subscriptions (User Admin'ning Getolog obunasi)
| Ustun | Tur | Tavsif |
|-------|-----|--------|
| id | SERIAL PK | Ichki ID |
| user_admin_id | FK → user_admins | Kim obuna bo'lgan |
| plan | ENUM('free','1month','6month','12month') | Tarif turi |
| started_at | TIMESTAMP DEFAULT NOW | Obuna boshlanishi |
| expires_at | TIMESTAMP NULL | Obuna tugashi (NULL=free) |
| amount_paid | DECIMAL(12,2) DEFAULT 0 | To'langan summa |
| status | ENUM('active','expired') | Obuna holati |
| notified_3day | BOOLEAN DEFAULT FALSE | 3 kun ogohlantirish |
| notified_1day | BOOLEAN DEFAULT FALSE | 1 kun ogohlantirish |

---

## 7. Fayl strukturasi

```
getolog/
├── main.py                     # Entry point — aiohttp server + barcha botlarni ishga tushiradi
├── config.py                   # Sozlamalar (env vars: DB, Redis, bot token, encryption key)
├── requirements.txt            # Python kutubxonalar
├── .env.example                # Environment variables namunasi
│
├── bot/                        # Asosiy GETOLOG bot
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py            # /start — ro'yxatdan o'tish
│   │   ├── register.py         # Token yuborish, validatsiya, bot yaratish
│   │   ├── settings.py         # Bot sozlamalari
│   │   ├── subscription.py     # Tarif tanlash, to'lov
│   │   ├── stats.py            # Statistika
│   │   ├── manage_users.py     # End userlarni boshqarish
│   │   └── support.py          # Support xabarlar
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py           # Tugmalar
│   └── middlewares/
│       ├── __init__.py
│       ├── i18n.py             # Ko'p tillilik
│       ├── ban_check.py        # Ban tekshirish
│       └── rate_limit.py       # Spam himoya (Redis orqali)
│
├── user_bot/                   # Generatsiya qilinadigan bot logikasi
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py            # End user /start
│   │   ├── language.py         # Til tanlash
│   │   ├── payment.py          # To'lov flow
│   │   ├── support.py          # Adminga xabar yuborish
│   │   └── callback.py         # Click/Payme callback'lar (MVP'dan keyin)
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py           # End user tugmalari
│   └── middlewares/
│       ├── __init__.py
│       ├── ad_inject.py        # Bepul tarifdagi reklama
│       └── rate_limit.py       # Spam himoya
│
├── moderator/                  # Moderator panel
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── dashboard.py        # Umumiy statistika
│   │   ├── manage_admins.py    # Admin'larni boshqarish
│   │   ├── manage_subs.py      # Obunalarni boshqarish
│   │   └── payments.py         # To'lovlarni ko'rish
│   └── keyboards/
│       └── inline.py
│
├── services/                   # Biznes logika (handler'dan ajratilgan)
│   ├── __init__.py
│   ├── admin_service.py        # User Admin: ro'yxatdan o'tish, sozlamalar
│   ├── bot_service.py          # Bot: yaratish, validatsiya, start/stop
│   ├── payment_service.py      # To'lov: yaratish, tasdiqlash, rad etish
│   ├── subscription_service.py # Obuna: yaratish, uzaytirish, tugatish
│   └── stats_service.py        # Statistika: to'lovlar, userlar, tushum
│
├── core/                       # Yadro funksiyalar
│   ├── __init__.py
│   ├── bot_manager.py          # Multi-bot boshqaruvchi (webhook)
│   ├── webhook_server.py       # aiohttp webhook server
│   ├── scheduler.py            # Cron vazifalar (APScheduler + Redis lock)
│   ├── invite_link.py          # Invite link yaratish/boshqarish
│   └── encryption.py           # Token shifrlash (Fernet)
│
├── db/                         # Database
│   ├── __init__.py
│   ├── engine.py               # SQLAlchemy async engine
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_admin.py
│   │   ├── user_bot.py
│   │   ├── channel.py
│   │   ├── end_user.py
│   │   ├── payment.py
│   │   ├── subscription.py
│   │   └── admin_subscription.py
│   └── migrations/             # Alembic migrations
│       └── ...
│
├── i18n/                       # Tarjimalar
│   ├── uz.json
│   ├── en.json
│   └── ru.json
│
└── utils/
    ├── __init__.py
    ├── helpers.py
    └── constants.py
```

### 7.1 Eski versiyadan farqlari

| O'zgarish | Sabab |
|-----------|-------|
| `services/` papkasi **qo'shildi** | Biznes logikani handler'dan ajratish — kelajakda web panel, API qo'shish oson |
| `core/webhook_server.py` **qo'shildi** | Webhook qabul qiluvchi aiohttp server |
| `core/notifications.py` **olib tashlandi** | Bildirishnomalar to'g'ridan-to'g'ri handler'larda yuboriladi |
| `bot/middlewares/rate_limit.py` **qo'shildi** | Spam/abuse himoyasi (Redis counter) |
| `user_bot/middlewares/rate_limit.py` **qo'shildi** | End user spam himoyasi |

---

## 8. Scheduler vazifalari (Cron jobs)

```
┌───────────────────────────────────────────────────────┐
│              Scheduler Service                         │
│          (APScheduler + Redis distributed lock)        │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ⏰ Har 10 daqiqada (muhim — kechikish minimal):       │
│  ├── End user kanaldan chiqarish (muddat tugdi)       │
│  └── Admin obuna tugatish → bepul tarifga o'tkazish   │
│                                                       │
│  ⏰ Har 6 soatda (ogohlantirish — tez bo'lishi shart   │
│     emas):                                            │
│  ├── Admin obuna ogohlantirish (3 kun qoldi)          │
│  ├── Admin obuna ogohlantirish (1 kun qoldi)          │
│  ├── End user muddat ogohlantirish (3 kun qoldi)      │
│  ├── End user muddat ogohlantirish (1 kun qoldi)      │
│  └── Bot health check (alive/dead tekshirish)         │
│                                                       │
│  ⏰ Server qayta ishga tushganda:                      │
│  └── Barcha aktiv botlar webhook qayta o'rnatish      │
│                                                       │
│  🔒 Redis lock:                                        │
│  └── Har bir task uchun distributed lock — duplicate   │
│      ishlanishini oldini oladi                         │
│                                                       │
└───────────────────────────────────────────────────────┘
```

### 8.1 Eski versiyadan farqlari

| O'zgarish | Sabab |
|-----------|-------|
| Kick/tugatish: 1 soat → **10 daqiqa** | Foydalanuvchi 59 daqiqa kechikmaslik uchun |
| Ogohlantirish: 1 soat → **6 soat** | Ogohlantirish tez bo'lishi shart emas, resurs tejash |
| **Redis distributed lock** qo'shildi | Duplicate task oldini olish |
| **Bot health check** qo'shildi | O'lik botlarni aniqlash va qayta ishga tushirish |

---

## 9. Xavfsizlik

| Element | Yechim |
|---------|--------|
| Bot tokenlari | Fernet symmetric encryption bilan database'da saqlanadi |
| Token validatsiya | `bot.get_me()` orqali token haqiqiyligini tekshirish — qabul qilishdan oldin |
| Invite linklar | Telegram API orqali bir martalik link (member_limit=1) |
| Admin autentifikatsiya | Telegram user ID orqali (bot token egasi) |
| Moderator autentifikatsiya | config.py da MODERATOR_IDS ro'yxati (list) |
| Database | SSL ulanish, environment variable'larda credentials |
| SQL Injection | SQLAlchemy ORM — parametrized query'lar |
| Rate limiting | Redis counter — har bir user uchun soniyada max 3 so'rov |
| Graceful error handling | Bitta bot xatosi boshqa botlarga ta'sir qilmaydi (try/except) |
| Monitoring | Sentry orqali barcha xatolar real-time kuzatiladi |

### 9.1 Eski versiyadan farqlari

| O'zgarish | Sabab |
|-----------|-------|
| **Token validatsiya** qo'shildi | Noto'g'ri/o'chirilgan token xavfini bartaraf etish |
| MODERATOR_ID → **MODERATOR_IDS (list)** | Kelajakda bir nechta moderator qo'shish imkoni |
| **Rate limiting** qo'shildi | Spam va abuse hujumlarini oldini olish |
| **Graceful error handling** qo'shildi | Bitta bot butun tizimni tushirmasligi uchun |
| **Sentry monitoring** qo'shildi | Xatolarni real-time kuzatish (bepul) |

---

## 10. Bildirishnomalar matritsasi

Bildirishnomalar to'g'ridan-to'g'ri handler'larda Telegram orqali yuboriladi (alohida jadval kerak emas).

| Hodisa | Moderator | User Admin | End User |
|--------|-----------|------------|----------|
| Yangi User Admin ro'yxatdan o'tdi | ✅ | — | — |
| User Admin obunasi 3 kun qoldi | ✅ | ✅ | — |
| User Admin obunasi 1 kun qoldi | ✅ | ✅ | — |
| User Admin obunasi tugadi | ✅ | ✅ | — |
| Yangi End User /start bosdi | — | ✅ | — |
| Yangi to'lov keldi (tasdiqlash kutilmoqda) | — | ✅ | — |
| To'lov tasdiqlandi | — | — | ✅ |
| To'lov rad etildi | — | — | ✅ |
| End User kanalga qo'shildi | — | ✅ | — |
| End User muddati 3 kun qoldi | — | — | ✅ |
| End User muddati 1 kun qoldi | — | — | ✅ |
| End User kanaldan chiqarildi | — | ✅ | ✅ |
| Bot crash / xatolik | ✅ (Sentry) | — | — |

---

## 11. Tillar tizimi (i18n)

3 til qo'llab-quvvatlanadi: **O'zbekcha (UZ)**, **Inglizcha (EN)**, **Ruscha (RU)**

- End User bot'ga /start bosganda til tanlaydi
- User Admin Getolog bot'da til tanlaydi
- Barcha xabarlar, tugmalar, bildirishnomalar tarjima qilinadi
- JSON fayllarda saqlanadi (i18n/uz.json, en.json, ru.json)
- aiogram middleware orqali har bir so'rovda til aniqlanadi

---

## 12. MVP — Birinchi versiya rejasi

### MVP'ga kiradi:
- [x] Getolog asosiy bot — User Admin ro'yxatdan o'tish
- [x] Token qabul qilish → validatsiya → bot generatsiya
- [x] User Admin sozlamalari (narx, muddat, karta)
- [x] End User flow — /start → til → narx → karta to'lov → link
- [x] Manual to'lov tasdiqlash (Admin tomonidan)
- [x] Bir martalik invite link
- [x] Kanaldan avtomatik chiqarish (muddat tugash)
- [x] Bildirishnomalar tizimi
- [x] Statistika (User Admin + Moderator)
- [x] 3 til (UZ/EN/RU)
- [x] Moderator panel (Telegram ichida)
- [x] Bepul tarifda reklama
- [x] Webhook arxitektura
- [x] Redis (FSM, cache, rate limit)
- [x] Sentry monitoring
- [x] Rate limiting (spam himoya)

### MVP'dan keyin:
- [ ] Click/Payme/Uzum integratsiyasi
- [ ] Web admin panel
- [ ] Referral tizim
- [ ] Kengaytirilgan statistika va analytics

---

## 13. Deployment

```bash
# DigitalOcean Droplet ($6/oy)
# Ubuntu 22.04 LTS, 1GB RAM, 1 vCPU

# 1. Server sozlash
apt update && apt upgrade -y
apt install python3.11 python3-pip redis-server nginx -y

# 2. Redis ishga tushirish
systemctl enable redis-server
systemctl start redis-server

# 3. Loyihani clone qilish
git clone <repo> /opt/getolog
cd /opt/getolog
pip install -r requirements.txt

# 4. Environment variables
cp .env.example .env
# .env ichiga yozish:
#   BOT_TOKEN=xxxx
#   DATABASE_URL=postgresql+asyncpg://user:pass@host/db
#   REDIS_URL=redis://localhost:6379/0
#   ENCRYPTION_KEY=xxxx (Fernet.generate_key())
#   MODERATOR_IDS=123456789,987654321
#   SERVER_URL=https://yourdomain.com
#   SENTRY_DSN=https://xxxx@sentry.io/xxxx

# 5. Database migration
alembic upgrade head

# 6. Nginx reverse proxy (webhook uchun SSL kerak)
# /etc/nginx/sites-available/getolog
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /webhook/ {
        proxy_pass http://127.0.0.1:8443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 7. SSL sertifikat (bepul)
apt install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com

# 8. Systemd service
# /etc/systemd/system/getolog.service
[Unit]
Description=Getolog Bot Service
After=network.target redis-server.service

[Service]
Type=simple
User=getolog
WorkingDirectory=/opt/getolog
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5
EnvironmentFile=/opt/getolog/.env

[Install]
WantedBy=multi-user.target

# 9. Start
systemctl enable getolog
systemctl start getolog
```

---

## 14. Resurs hisob-kitobi

| Komponent | Narx |
|-----------|------|
| DigitalOcean Droplet (1GB RAM, 1 vCPU) | $6/oy |
| PostgreSQL (Neon Free Tier) | $0/oy |
| Redis (serverda local) | $0/oy |
| Sentry (Free Tier) | $0/oy |
| SSL sertifikat (Let's Encrypt) | $0/oy |
| Domain | ~$10/yil (~$0.8/oy) |
| **Jami** | **~$6-7/oy** |

### RAM taqsimoti (1GB server)

```
┌──────────────────────────────────────────┐
│          1GB RAM taqsimoti               │
├──────────────────────────────────────────┤
│  OS + Nginx           ~150MB             │
│  Python process       ~100MB             │
│  Redis                ~50MB              │
│  Webhook botlar (100) ~100MB             │
│  Scheduler            ~50MB              │
│  ─────────────────────────               │
│  Zaxira               ~550MB             │
│                                          │
│  Webhook = 100+ bot sig'adi              │
│  (Polling bo'lganda faqat 50 sig'ardi)   │
└──────────────────────────────────────────┘
```

### Scale rejasi

| Bosqich | Botlar | Server | Narx |
|---------|--------|--------|------|
| Boshlang'ich | 1-100 | 1GB Droplet | $6/oy |
| O'sish | 100-300 | 2GB Droplet | $12/oy |
| Katta | 300+ | 4GB Droplet yoki 2 ta server | $24/oy |

---

## 15. Ishlab chiqish tartibi (Development Roadmap)

Kodlash quyidagi ketma-ketlikda amalga oshiriladi:

| Tartib | Modul | Tavsif |
|--------|-------|--------|
| 1 | `config.py` + `.env.example` | Sozlamalar va env vars |
| 2 | `db/engine.py` + `db/models/` | Database modellar va ulanish |
| 3 | `core/encryption.py` | Fernet shifrlash moduli |
| 4 | `core/webhook_server.py` | aiohttp webhook server |
| 5 | `services/` | Biznes logika servislari |
| 6 | `bot/handlers/start.py` + `register.py` | Asosiy bot — ro'yxatdan o'tish |
| 7 | `core/bot_manager.py` | Multi-bot boshqaruvchi |
| 8 | `user_bot/handlers/` | End user to'lov flow |
| 9 | `core/invite_link.py` | Invite link yaratish |
| 10 | `core/scheduler.py` | Cron vazifalar |
| 11 | `moderator/handlers/` | Moderator panel |
| 12 | `i18n/` | Ko'p tillilik |
| 13 | `bot/middlewares/rate_limit.py` | Rate limiting |
| 14 | Sentry integratsiya | Error monitoring |

---

## 16. requirements.txt

```
aiogram==3.x
aiohttp==3.x
sqlalchemy[asyncio]==2.x
asyncpg==0.x
alembic==1.x
redis[hiredis]==5.x
apscheduler==3.x
cryptography==42.x
sentry-sdk==1.x
pydantic==2.x
python-dotenv==1.x
```

---

*Hujjat versiyasi: 2.1 (Tasdiqlangan)*
*Yangilangan: 2026-02-07*
*Loyiha: GETOLOG*
*v2.0: Webhook arxitektura, Redis, Sentry, DB schema tuzatishlar, rate limiting, graceful error handling*
*v2.1: Service layer qo'shildi — biznes logika handler'dan ajratildi (kelajakda web panel, API uchun tayyor)*
