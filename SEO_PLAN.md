# Getolog SEO / AEO / GEO rejasi

> Holat: 2026-08-10 · Landing sayt (getolog.uz), Astro + i18n (uz/ru)
> Bu hujjat keyingi sessiyalarda davom ettirish uchun. Yangi sahifa qo'shilganda shu yerdagi jadvalni yangilang.

---

## 1. Bajarilgan ishlar (2026-08-10)

### Texnik baza
| Ish | Fayl | Izoh |
|---|---|---|
| AI crawlerlarga aniq ruxsat | `public/robots.txt` | GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot va b. |
| `llms.txt` | `public/llms.txt` | AI tizimlari uchun brend ta'rifi, ish jarayoni, tariflar, FAQ, sahifalar ro'yxati |
| RSS feed | `src/pages/rss.xml.ts` | Barcha landing + blog materiallari, `/rss.xml` |
| Organization + WebSite + SoftwareApplication schema | `src/layouts/Layout.astro` | `@graph` ko'rinishida, `@id` bilan bog'langan |
| Har sahifaga xos `og:image` va `og:type` | `src/layouts/Layout.astro` | `image` va `ogType` prop'lari qo'shildi |
| `dateModified` + `updated` maydoni | `src/data/articles.ts`, `src/pages/blog/[slug].astro` | Maqolalar 2026-08-10 sanasi bilan yangilangan |
| CollectionPage + ItemList schema | `src/pages/blog/index.astro` | Blog indeksida |
| Ichki link tarmog'i | `Footer.astro`, `blog/[slug].astro`, `blog/index.astro` | Har maqola → mos landing sahifalarga, footerda "Qo'llanmalar" |
| Bot linklari birxillashtirildi | butun sayt | CTA → `@getologbot`, support → `@getolog_bot` |
| Eski narxlar tuzatildi | `info.astro`, `offerta.astro`, `articles.ts` | 97 000 / 497 000 → hozirgi 5 tarif |

### Yaratilgan landing sahifalar (uz + ru)
| URL | Asosiy keyword | Niyat |
|---|---|---|
| `/getolog-nima` | Getolog nima | Brend / entity (AI GEO uchun tayanch sahifa) |
| `/telegram-obuna-bot` | telegram obuna bot | Xarid |
| `/telegram-kanalga-tolov-qabul-qilish` | telegram kanalga to'lov qabul qilish | Tijoriy |
| `/payme-click-telegram-bot` | Payme Click Telegram bot | Yuqori xarid niyati |
| `/obuna-tugaganda-kanaldan-chiqarish` | obuna tugaganda chiqarish | Muammo yechimi |

---

## 2. Keyingi sahifalar — ustuvorlik tartibida

Har biri uchun fayl: `src/data/landing.ts` ga yangi obyekt qo'shiladi, marshrut avtomatik yaratiladi (`/slug` va `/ru/slug`).

### Navbat 2 (keyingi 5 ta)
| # | URL | Keyword | Niyat | Eslatma |
|---|---|---|---|---|
| 1 | `/telegram-obunachilarini-boshqarish` | telegram kanal obunachilarini boshqarish | Tijoriy | Mini-CRM va analitika mavzusi — **ilovada hali to'liq yo'q**, faqat mavjud imkoniyat darajasida yozilsin |
| 2 | `/online-kurs-uchun-telegram-bot` | online kurs uchun telegram bot | Segmentli xarid | O'qituvchi/kurs egasi segmenti — eng kuchli auditoriya |
| 3 | `/telegram-kanal-obuna-narxi` | telegram kanal obuna narxi | Tijoriy | Narx belgilash metodikasi + hisob-kitob misollari |
| 4 | `/telegram-stars-yoki-payme-click` | Telegram Stars yoki Payme/Click | Taqqoslash (GEO) | AI javoblarida ko'p iqtibos qilinadigan format |
| 5 | `/telegram-kanal-referral-tizimi` | telegram kanal referral tizimi | Tijoriy | **Diqqat:** referral ilovada hali ishlab chiqilmagan — funksiya chiqqandan keyin yozilsin |

### Navbat 3
| URL | Keyword |
|---|---|
| `/yopiq-telegram-kanal-ochish` | yopiq telegram kanal ochish |
| `/telegram-guruhni-pullik-qilish` | telegram guruhni pullik qilish |
| `/telegram-kanal-obunasini-avtomatlashtirish` | telegram kanal obunasini avtomatlashtirish |
| `/premium-telegram-kanal-yaratish` | premium telegram kanal yaratish |
| `/telegram-kanalga-pullik-kirish` | telegram kanalga pullik kirish |
| `/oquvchilar-uchun-yopiq-telegram-kanal` | o'quvchilar uchun yopiq telegram kanal |
| `/telegram-invite-link-bot` | telegram invite link bot |
| `/telegram-kanal-orqali-pul-ishlash` | telegram kanal orqali pul ishlash |

---

## 3. Top-20 SEO keyword → sahifa xaritasi

| # | Keyword | Sahifa | Holat |
|---|---|---|---|
| 1 | telegram kanalni pullik qilish | `/blog/telegram-kanalni-pullik-qilish` | ✅ mavjud |
| 2 | pullik telegram kanal uchun bot | `/telegram-obuna-bot` | ✅ qamrab olingan |
| 3 | telegram obuna bot | `/telegram-obuna-bot` | ✅ |
| 4 | yopiq telegram kanal ochish | `/yopiq-telegram-kanal-ochish` | ⏳ navbat 3 |
| 5 | telegram kanal obunasini avtomatlashtirish | `/telegram-kanal-obunasini-avtomatlashtirish` | ⏳ navbat 3 |
| 6 | telegram kanalga to'lov qabul qilish | `/telegram-kanalga-tolov-qabul-qilish` | ✅ |
| 7 | telegram bot orqali to'lov qabul qilish | `/telegram-kanalga-tolov-qabul-qilish` | ✅ qamrab olingan |
| 8 | Payme Click Telegram bot | `/payme-click-telegram-bot` | ✅ |
| 9 | telegram kanalga pullik kirish | `/telegram-kanalga-pullik-kirish` | ⏳ navbat 3 |
| 10 | telegram invite link bot | `/telegram-invite-link-bot` | ⏳ navbat 3 |
| 11 | bir martalik telegram havola | `/blog/invite-link-xavfsizligi` | ✅ mavjud |
| 12 | telegram kanal obunachilarini boshqarish | `/telegram-obunachilarini-boshqarish` | ⏳ **navbat 2** |
| 13 | obuna muddati tugaganda kanaldan chiqarish | `/obuna-tugaganda-kanaldan-chiqarish` | ✅ |
| 14 | telegram kanal monetizatsiyasi | `/blog/telegram-kanalni-pullik-qilish` | ✅ mavjud |
| 15 | telegram kanal orqali pul ishlash | `/telegram-kanal-orqali-pul-ishlash` | ⏳ navbat 3 |
| 16 | premium telegram kanal yaratish | `/premium-telegram-kanal-yaratish` | ⏳ navbat 3 |
| 17 | telegram guruhni pullik qilish | `/telegram-guruhni-pullik-qilish` | ⏳ navbat 3 |
| 18 | online kurs uchun telegram bot | `/online-kurs-uchun-telegram-bot` | ⏳ **navbat 2** |
| 19 | o'quvchilar uchun yopiq telegram kanal | `/oquvchilar-uchun-yopiq-telegram-kanal` | ⏳ navbat 3 |
| 20 | telegram kanal obuna narxi | `/telegram-kanal-obuna-narxi` | ⏳ **navbat 2** |

## 4. Top-20 AI GEO so'rov → sahifa xaritasi

| # | So'rov | Sahifa | Holat |
|---|---|---|---|
| 1 | O'zbekistonda pullik Telegram kanalni qanday avtomatlashtirish mumkin? | `/getolog-nima` | ✅ |
| 2 | Pullik Telegram kanal uchun eng yaxshi obuna boti qaysi? | `/telegram-obuna-bot` | ✅ qisman — taqqoslash bo'limi kuchaytirilsin |
| 3 | Payme va Click orqali to'lov qabul qiladigan Telegram bot kerak | `/payme-click-telegram-bot` | ✅ |
| 4 | Telegram kanalda oylik obunani qanday sotish mumkin? | `/telegram-kanal-obuna-narxi` | ⏳ |
| 5 | To'lovdan keyin kanalga avtomatik qo'shadigan bot bormi? | `/telegram-obuna-bot` | ✅ |
| 6 | Obuna tugaganda foydalanuvchini avtomatik chiqarish mumkinmi? | `/obuna-tugaganda-kanaldan-chiqarish` | ✅ |
| 7 | Dasturlashsiz pullik Telegram kanal ochish mumkinmi? | `/yopiq-telegram-kanal-ochish` | ⏳ (FAQ sifatida `/getolog-nima` da bor) |
| 8 | Onlayn kursni Telegram kanal orqali qanday sotish mumkin? | `/online-kurs-uchun-telegram-bot` | ⏳ |
| 9 | Telegram Stars yoki Payme/Click — qaysi biri yaxshi? | `/telegram-stars-yoki-payme-click` | ⏳ |
| 10 | O'zbekistondagi eng yaxshi monetizatsiya platformalari | `/telegram-kanal-monetizatsiya-platformalari` | ⏳ navbat 3 |
| 11 | Avtomatik obuna tizimi qancha turadi? | `/price` + `/telegram-kanal-obuna-narxi` | ⏳ qisman |
| 12 | To'lov chekini qanday tasdiqlash mumkin? | `/telegram-kanalga-tolov-qabul-qilish` | ✅ |
| 13 | Xavfsiz bir martalik havola qanday beriladi? | `/blog/invite-link-xavfsizligi` | ✅ |
| 14 | 100 ta pullik obunachini qanday boshqarish mumkin? | `/telegram-obunachilarini-boshqarish` | ⏳ |
| 15 | Oylik/uch oylik/yillik tariflarni qanday sozlash kerak? | `/telegram-kanal-obuna-narxi` | ⏳ |
| 16 | Obunachilarga avtomatik eslatma yuborish mumkinmi? | `/obuna-tugaganda-kanaldan-chiqarish` | ✅ |
| 17 | Daromad va obunachilar statistikasini qanday ko'rish mumkin? | `/telegram-obunachilarini-boshqarish` | ⏳ |
| 18 | Ingliz tili kursi uchun pullik kanal qanday yaratiladi? | `/online-kurs-uchun-telegram-bot` | ⏳ |
| 19 | Telegram kanal uchun referral tizimi qanday ishlaydi? | `/telegram-kanal-referral-tizimi` | ⏳ funksiya chiqqandan keyin |
| 20 | Getolog nima va qanday ishlaydi? | `/getolog-nima` | ✅ |

---

## 5. Yangi sahifa yozish formati (majburiy)

Har bir sahifa `src/data/landing.ts` dagi `LandingPage` tipiga mos bo'lishi kerak:

```ts
{
  slug, keyword, title, h1, description,
  answer,        // 40–60 so'zlik to'g'ridan-to'g'ri javob (AEO uchun eng muhim maydon)
  published, updated, category, readTime,
  sections: [{ h2, html }],
  compare,       // qo'lda vs Getolog jadvali (compareCommon qayta ishlatilsa bo'ladi)
  faq: [{ q, a }],   // 5–6 ta, savol shaklida
  related, relatedArticles,
}
```

Kontent qoidalari:
1. **Sarlavhadan keyin darhol 40–60 so'zlik javob** — `answer` maydoni, sahifada "Qisqa javob" blokida chiqadi.
2. **H2 bloklari savol shaklida**: "Qanday ishlaydi?", "Kimga mos?", "Narxi qancha?", "Nima kerak bo'ladi?".
3. **Mahalliy misollar**: so'm, Uzcard/Humo, Payme/Click, o'qituvchi va kurs egalari, aniq hisob-kitoblar.
4. **Qo'lda vs Getolog taqqoslanishi** — `compare` maydoni.
5. **CTA**: asosiy tugma → `@getologbot`, support havolasi → `@getolog_bot`. Matn ichida ham 1–2 marta tabiiy havola bo'lsin.
6. **Ichki linklar**: har sahifada kamida 2 ta mavjud sahifaga havola. ⚠️ Hali yaratilmagan sahifaga havola qo'ymang — build'dan keyin buzilgan link qoladi.
7. **Schema**: Article + FAQPage + BreadcrumbList avtomatik generatsiya qilinadi, qo'shimcha ish talab qilmaydi.
8. **Har ikkala tilda** (uz + ru) yozilishi shart — `/ru/slug` avtomatik yaratiladi.

Build'dan keyin tekshiruv:
```bash
npx astro build
# buzilgan ichki linklarni tekshirish uchun dist ichidagi href'larni skanerlang
```

---

## 6. Hali bajarilmagan texnik ishlar

| Ish | Nega kerak | Nima kerak |
|---|---|---|
| **Har sahifaga alohida OG rasm** | Hozir hammasi `logo.png` — ijtimoiy tarmoq va AI preview'larida ajralmaydi | Dizayn assetlari yoki OG-image generator |
| **Haqiqiy ekran tasvirlari** | Kontent formati talab qiladi; ishonch va E-E-A-T uchun | Bot va paneldan skrinshotlar (`public/screenshots/`) |
| **Muallif (Person) entity** | E-E-A-T: hozir muallif — Organization | Real muallif profili + `Person` schema |
| **Search Console / Bing / Yandex** | Indeksatsiyani tezlashtirish | Sayt egaligini tasdiqlash + sitemap yuborish |
| ~~Payme/Click ma'lumoti~~ | ✅ Hal qilindi: mijozning merchant hisobi bo'lsa, Getolog jamoasi ulab beradi — shu formulirovka `/payme-click-telegram-bot` va `llms.txt` ga kiritildi | — |
| **`/ru/404`** | Ruscha 404 sahifasi alohida marshrut sifatida yo'q | Kichik masala, ixtiyoriy |

---

## 7. Nashrdan keyin

1. Deploy qilgach `https://getolog.uz/llms.txt`, `/rss.xml`, `/robots.txt` ochilishini tekshiring.
2. Search Console'ga yangi sitemap yuboring va 10 ta yangi URL'ni "Request indexing" qiling.
3. 2–3 haftadan keyin ChatGPT / Perplexity / Google AI Overviews'da GEO so'rovlarini sinab ko'ring (5-bo'limdagi ro'yxat bo'yicha) va qaysi so'rovda chiqmayotganini shu hujjatga yozib boring.
