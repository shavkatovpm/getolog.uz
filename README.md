# Getolog — Telegram kanal monetizatsiya platformasi

**Getolog** — Telegram kanal va guruh egalariga o'z kontentini pullik qilish imkonini beruvchi SaaS platforma. Admin o'z bot tokenini yuboradi — Getolog uning asosida avtomatlashtirilgan "sotuvchi bot" yaratadi, u to'lovlarni qabul qiladi, invite link beradi va obunani boshqaradi.

## Qanday ishlaydi?

```
Admin bot yaratadi → Foydalanuvchi to'lov qiladi → Admin tasdiqlaydi → Foydalanuvchi kanalga kiradi
```

### To'liq flow

1. **Admin** @getolog_bot ga `/start` bosadi
2. Bot tokenini yuboradi (BotFather dan olingan)
3. Karta raqamini kiritadi (to'lov qabul qilish uchun)
4. Botni kanalga admin qilib qo'shadi — kanal avtomatik aniqlanadi
5. Narx va obuna muddatini belgilaydi
6. Bot ishga tushadi — foydalanuvchilar obuna bo'la boshlaydi

### Foydalanuvchi (End User) flow

1. Admin yaratgan botga `/start` bosadi
2. Tilni tanlaydi (UZ/RU/EN)
3. Mavjud kanallarni ko'radi
4. "Sotib olish" bosadi → Admin karta raqamini ko'radi
5. Pul o'tkazadi → Skrinshot yuboradi
6. Admin tasdiqlaydi → Bir martalik invite link keladi
7. Kanalga kiradi
8. Muddat tugashi yaqinlashganda ogohlantirish keladi
9. Muddat tugaganda avtomatik chiqariladi

---

## Loyiha tuzilmasi

```
getolog.uz/
├── src/                          # Frontend (Astro)
│   ├── pages/
│   │   ├── index.astro           # Bosh sahifa
│   │   ├── price.astro           # Narxlar taqqoslash jadvali
│   │   └── 404.astro             # 404 sahifa
│   ├── components/               # UI komponentlar
│   │   ├── Navbar.astro
│   │   ├── Hero.astro
│   │   ├── Problems.astro
│   │   ├── HowItWorks.astro
│   │   ├── Pricing.astro
│   │   ├── FAQ.astro
│   │   ├── CTA.astro
│   │   └── Footer.astro
│   ├── layouts/Layout.astro
│   └── styles/global.css
│
├── backend/
│   ├── main.py                   # Entry point
│   ├── config.py                 # Konfiguratsiya
│   │
│   ├── bot/                      # Asosiy Getolog bot
│   │   ├── handlers/
│   │   │   ├── start.py          # /start, bot tanlash
│   │   │   ├── register.py       # Bot yaratish (token → karta → kanal → narx)
│   │   │   ├── subscription.py   # Tarif rejalar (Free/Standard/Premium)
│   │   │   ├── payments.py       # To'lovlarni tasdiqlash/rad etish
│   │   │   ├── stats.py          # Statistika
│   │   │   ├── settings.py       # Sozlamalar + hamkorlar
│   │   │   └── manage_users.py   # Foydalanuvchilar boshqaruvi
│   │   ├── keyboards/inline.py   # Inline tugmalar
│   │   ├── middlewares/           # Ban tekshiruvi, rate limit
│   │   └── helpers.py            # Yordamchi funksiyalar
│   │
│   ├── user_bot/                 # Foydalanuvchi botlari (shablon)
│   │   ├── handlers/
│   │   │   ├── start.py          # /start, til tanlash, kanal ko'rish
│   │   │   └── payment.py        # To'lov qilish, skrinshot yuborish
│   │   ├── keyboards/
│   │   └── middlewares/
│   │       └── ad_inject.py      # Getolog brending (Free/Standard)
│   │
│   ├── moderator/                # Moderator paneli
│   │   └── handlers/             # Adminlarni boshqarish
│   │
│   ├── core/
│   │   ├── bot_manager.py        # Multi-bot webhook orkestratsiya
│   │   ├── webhook_server.py     # aiohttp server
│   │   ├── scheduler.py          # APScheduler vazifalari
│   │   ├── encryption.py         # Fernet shifrlash (token, karta)
│   │   ├── cache.py              # Redis kesh
│   │   └── invite_link.py        # Bir martalik invite linklar
│   │
│   ├── db/
│   │   ├── models/               # 9 ta SQLAlchemy model
│   │   ├── engine.py             # Async session
│   │   └── base.py               # Base class
│   │
│   ├── services/                 # Biznes logika
│   │   ├── bot_service.py        # Bot CRUD, kanal boshqaruvi
│   │   ├── payment_service.py    # To'lov yaratish/tasdiqlash
│   │   ├── subscription_service.py # Obuna yaratish/tekshirish
│   │   ├── admin_service.py      # Admin akkauntlar
│   │   └── stats_service.py      # Statistika
│   │
│   ├── api/                      # WebApp Mini App API
│   │   ├── auth.py               # Telegram WebApp autentifikatsiya
│   │   ├── middleware.py          # CORS, rate limiting
│   │   ├── routes_stats.py       # GET /api/stats
│   │   ├── routes_payments.py    # To'lovlar CRUD
│   │   ├── routes_users.py       # Foydalanuvchilar + ban
│   │   ├── routes_settings.py    # Sozlamalar CRUD
│   │   └── routes_messaging.py   # Xabar yuborish, broadcast
│   │
│   ├── webapp/                   # Telegram Mini App (HTML/JS/CSS)
│   ├── utils/
│   │   ├── constants.py          # FSM states, StrEnum enumlar
│   │   └── validators.py         # Karta validatsiya (Luhn)
│   ├── i18n/                     # Tillar (uz, ru, en)
│   ├── migrations/               # Alembic migratsiyalar
│   ├── tests/                    # Unit testlar (27 ta)
│   └── requirements.txt
│
├── package.json                  # Frontend dependencies
└── astro.config.mjs
```

---

## Foydalanuvchi rollari

| Rol | Tavsif |
|-----|--------|
| **Moderator** | Platforma admini — adminlarni boshqaradi, tariflarni tasdiqlaydi |
| **Admin** | Kanal egasi — bot yaratadi, to'lovlarni tasdiqlaydi |
| **Hamkor (Collaborator)** | Admin yordamchisi — to'lovlarni ko'radi va tasdiqlaydi |
| **End User** | Oddiy foydalanuvchi — kanalga obuna bo'ladi |

---

## Tarif rejalar

| Xususiyat | Free | Standard | Premium |
|-----------|------|----------|---------|
| Bot limiti | 1 | 2 | 5 |
| Ko'p admin (hamkor) | — | 2 ta | 5 ta |
| Reklama (brending) | Bor | Yo'q | Yo'q |
| Getolog brending | Bor | Bor | Yo'q |
| Click/Payme | — | — | Bor |
| **Narx** | **Bepul** | **97,000 UZS/oy** | **197,000 UZS/oy** |

---

## Ma'lumotlar bazasi modellari

### Asosiy jadvallar (9 ta)

| Model | Tavsif |
|-------|--------|
| `UserAdmin` | Platforma foydalanuvchilari (bot yaratuvchilar) |
| `UserBot` | Yaratilgan botlar (token shifrlangan, karta shifrlangan) |
| `Channel` | Pullik kanallar/guruhlar (narx, muddat) |
| `EndUser` | Bot foydalanuvchilari (har bot uchun alohida) |
| `Payment` | To'lov yozuvlari (summa, status, skrinshot) |
| `Subscription` | Faol obunalar (invite link, muddat, status) |
| `AdminSubscription` | Getolog tarif obunalari (free/standard/premium) |
| `BotCollaborator` | Hamkorlar (ko'p admin) |

### Bog'lanishlar

```
UserAdmin ──┬── UserBot ──┬── Channel ──── Subscription
            │             ├── EndUser ──┬── Payment ──── Subscription
            │             └── BotCollaborator
            └── AdminSubscription
```

---

## API endpointlar (WebApp Mini App)

Barcha endpointlar Telegram WebApp `initData` orqali autentifikatsiya qilinadi (HMAC-SHA256).

| Metod | Yo'l | Tavsif |
|-------|------|--------|
| GET | `/api/stats` | Statistika (daromad, foydalanuvchilar, to'lovlar) |
| GET | `/api/payments` | Kutilayotgan to'lovlar |
| GET | `/api/payments/{id}/screenshot` | Skrinshot URL |
| POST | `/api/payments/{id}/approve` | To'lovni tasdiqlash |
| POST | `/api/payments/{id}/reject` | To'lovni rad etish |
| GET | `/api/users` | Foydalanuvchilar ro'yxati |
| POST | `/api/users/{id}/ban` | Foydalanuvchini bloklash |
| POST | `/api/users/{id}/unban` | Blokdan chiqarish |
| POST | `/api/users/{id}/message` | Xabar yuborish |
| POST | `/api/broadcast` | Ommaviy xabar (barcha foydalanuvchilarga) |
| GET | `/api/settings` | Bot sozlamalari |
| PUT | `/api/settings` | Sozlamalarni yangilash |

---

## Xavfsizlik

| Himoya | Tavsif |
|--------|--------|
| **Webhook xavfsizligi** | Token o'rniga HMAC-SHA256 hash URL da |
| **Token shifrlash** | Bot tokenlari Fernet bilan shifrlangan |
| **Karta shifrlash** | Karta raqamlari Fernet bilan shifrlangan |
| **CORS cheklash** | Faqat `https://web.telegram.org` ruxsat |
| **API rate limiting** | 30 so'rov/daqiqa har IP uchun |
| **WebApp auth** | Telegram initData HMAC-SHA256 tekshiruvi |
| **To'lov idempotency** | UniqueConstraint + row-level locking |
| **Luhn validatsiya** | Xalqaro kartalar uchun Luhn tekshiruvi |

---

## Scheduler vazifalari

| Vaqt oralig'i | Vazifa |
|---------------|--------|
| Har 10 daqiqa | Muddati tugagan foydalanuvchilarni kanaldan chiqarish |
| Har 10 daqiqa | Muddati tugagan admin tariflarni expire qilish |
| Har 6 soat | 3 kunlik ogohlantirish yuborish |
| Har 6 soat | 1 kunlik ogohlantirish yuborish |
| Har 6 soat | Bot health check + o'lik botlarni qayta ishga tushirish |

---

## Redis kesh

| Kalit | TTL | Ishlatilgan joy | Invalidation |
|-------|-----|----------------|--------------|
| `stats:{bot_id}` | 30s | API stats | To'lov tasdiqlanganda |
| `settings:{bot_id}` | 30s | API settings, bot sozlamalar | Sozlama o'zgarganda |
| `premium:{username}` | 120s | Ad inject middleware | Tarif o'zgarganda |
| `users:{bot_id}` | 30s | Foydalanuvchilar ro'yxati | Ban toggle da |

---

## Ishga tushirish

### Talablar
- Python 3.12+
- PostgreSQL
- Redis
- Node.js 18+ (frontend uchun)

### Environment o'zgaruvchilari

```env
BOT_TOKEN=123456:ABC...           # Asosiy bot token
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/getolog
REDIS_URL=redis://localhost:6379
ENCRYPTION_KEY=...                # Fernet kalit (python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
MODERATOR_IDS=123456789           # Moderator Telegram ID lari
SERVER_URL=https://getolog.uz     # Server URL
WEBHOOK_PORT=8443
ENV=production                    # production yoki development
SENTRY_DSN=...                    # Ixtiyoriy
```

### Backend

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python main.py
```

### Frontend

```bash
npm install
npm run build    # Production build
npm run dev      # Development server (localhost:4321)
```

---

## Testlar

```bash
cd backend
python -m pytest tests/ -v
```

27 ta test:
- `test_validators.py` — Karta validatsiya (Luhn, Uzcard, Humo)
- `test_encryption.py` — Token va karta shifrlash
- `test_webhook_secret.py` — Webhook hash xavfsizligi
- `test_constants.py` — StrEnum enumlar

---

## Texnologiyalar

| Komponent | Texnologiya |
|-----------|-------------|
| Bot framework | aiogram 3 |
| Web server | aiohttp |
| Database | PostgreSQL + SQLAlchemy (async) |
| Migrations | Alembic |
| Cache/FSM | Redis |
| Scheduler | APScheduler |
| Encryption | cryptography (Fernet) |
| Error tracking | Sentry |
| Frontend | Astro |
| Hosting | VPS + Webhook |
