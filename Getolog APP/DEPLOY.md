# GETOLOG — Deploy qo'llanmasi

Bu loyihada **git push orqali avtomatik deploy yo'q** — backend va dashboard alohida, qo'lda (yoki shu qo'llanmadagi buyruqlar bilan) joylashtiriladi. Sabab: backend oddiy VPS'da systemd xizmat sifatida, dashboard esa Vercel'da ishlaydi — ikkalasi ham git remote'ga bog'lanmagan alohida deploy oqimiga ega.

## Arxitektura

- **Backend** (`app/` — aiogram bot + aiohttp API): DigitalOcean droplet, `46.101.220.20`, hostname `Darslinker` (bu droplet'da **darslinker.uz** loyihasi ham ishlaydi — u yerga umuman tegilmasin, faqat `/opt/getolog` va unga tegishli nginx/systemd fayllari bilan ishlanadi).
- **Dashboard** (`dashboard/` — Next.js): Vercel, loyiha nomi `dashboard`, domen `app.getolog.uz`.
- **Webhook/API domeni**: `bot.getolog.uz` (droplet'ga yo'naltirilgan, nginx + Let's Encrypt SSL).

## Backend deploy

Server: `ssh root@46.101.220.20` (SSH kalit shu Mac'da allaqachon sozlangan).

Kod va bog'liqliklarni yangilash:

```bash
cd "Getolog APP"
rsync -az --exclude='.venv' --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' --exclude='dashboard' ./ root@46.101.220.20:/opt/getolog/
ssh root@46.101.220.20 "cd /opt/getolog && source .venv/bin/activate && pip install -q -r requirements.txt"
ssh root@46.101.220.20 "systemctl restart getolog"
```

Agar baza sxemasi o'zgargan bo'lsa (yangi Alembic migratsiya):

```bash
ssh root@46.101.220.20 "cd /opt/getolog && source .venv/bin/activate && alembic upgrade head"
```

**Muhim:** deploydan keyin har doim `curl -sS -o /dev/null -w "%{http_code}\n" https://darslinker.uz` bilan darslinker.uz'ga zarar yetmaganini tekshiring.

### Server tuzilishi

- Kod: `/opt/getolog`
- Muhit o'zgaruvchilari: `/opt/getolog/.env` (serverda, git'ga kirmaydi — qiymatlarni shu yerdan ko'ring)
- Systemd xizmat: `getolog.service` (`systemctl status getolog`, `journalctl -u getolog -f`)
- nginx: `/etc/nginx/sites-available/getolog` (faqat shu fayl — `darslinker` fayliga tegilmasin)
- Postgres: `getolog` bazasi, `getolog` foydalanuvchisi (mavjud Postgres instance ichida, boshqa bazalardan ajratilgan)

### Kerakli .env o'zgaruvchilari (qiymatlar serverda, bu yerda faqat ro'yxat)

`DATABASE_URL`, `ENCRYPTION_KEY`, `MAIN_BOT_TOKEN`, `OWNER_TELEGRAM_ID`, `WEBHOOK_BASE_URL`, `WEBHOOK_SERVER_PORT`, `JWT_SECRET_KEY`, `DASHBOARD_ORIGIN` — namuna uchun `.env.example`ga qarang.

## Dashboard deploy (Vercel)

```bash
cd "Getolog APP/dashboard"
vercel --prod --yes
```

Vercel CLI allaqachon shu Mac'da tizimga kirgan va loyiha (`dashboard`) bilan bog'langan (`.vercel/` papkasi — git'ga kirmaydi). Boshqa mashinada birinchi marta ishlatishda `vercel link` orqali loyihaga ulanish kerak bo'ladi.

Muhit o'zgaruvchilari (`NEXT_PUBLIC_API_BASE`, `NEXT_PUBLIC_BOT_USERNAME`) Vercel loyiha sozlamalarida (`vercel env ls` bilan ko'rish mumkin) — qiymatlarni o'zgartirish uchun `vercel env add <NOM> production`.

## Mahalliy ishga tushirish

- Backend: `.venv` (Python 3.12) + mahalliy Postgres (`getolog` bazasi) + `.env` fayl (root papkada, git'ga kirmaydi). `python -m app.main` bilan ishga tushadi.
- Dashboard: `npm run dev` (`dashboard/` papkasida), `.env.local` fayl kerak (`NEXT_PUBLIC_API_BASE`, `NEXT_PUBLIC_BOT_USERNAME`).
