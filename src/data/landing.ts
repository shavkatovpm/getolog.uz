import type { Lang } from "../i18n/translations";

type T = Record<Lang, string>;

export interface LandingFAQ {
  q: T;
  a: T;
}

export interface LandingSection {
  h2: T;
  html: T;
}

export interface CompareRow {
  label: T;
  manual: T;
  getolog: T;
}

export interface LandingPage {
  /** URL segmenti — sahifa saytning ildizida turadi: /slug */
  slug: string;
  /** Asosiy keyword — ichki hisobot va breadcrumb uchun */
  keyword: T;
  title: T;
  h1: T;
  description: T;
  /** AEO uchun 40–60 so'zlik to'g'ridan-to'g'ri javob */
  answer: T;
  published: string;
  updated: string;
  category: T;
  readTime: T;
  sections: LandingSection[];
  compare?: { title: T; rows: CompareRow[] };
  faq: LandingFAQ[];
  /** Boshqa landing sahifalar slug'lari */
  related: string[];
  /** Blog maqolalari slug'lari */
  relatedArticles?: string[];
}

/* Qo'lda boshqarish vs Getolog — sahifalarda qayta ishlatiladigan umumiy jadval */
const compareCommon = {
  title: {
    uz: "Qo'lda boshqarish va Getolog orqali avtomatlashtirish",
    ru: "Ручное управление и автоматизация через Getolog",
  } as T,
  rows: [
    {
      label: { uz: "To'lovni qabul qilish", ru: "Приём оплаты" } as T,
      manual: { uz: "Obunachi shaxsiy hisobingizga yozadi, chekni siz ko'rasiz", ru: "Подписчик пишет вам в личку, чек проверяете вы" } as T,
      getolog: { uz: "Bot rekvizitni beradi, chekni qabul qiladi, siz bir tugma bilan tasdiqlaysiz", ru: "Бот выдаёт реквизиты, принимает чек, вы подтверждаете одной кнопкой" } as T,
    },
    {
      label: { uz: "Kanalga kiritish", ru: "Добавление в канал" } as T,
      manual: { uz: "Havolani qo'lda yuborasiz — u tarqalib ketishi mumkin", ru: "Отправляете ссылку вручную — она может разойтись" } as T,
      getolog: { uz: "Bir martalik invite-link avtomatik yuboriladi", ru: "Одноразовая invite-ссылка отправляется автоматически" } as T,
    },
    {
      label: { uz: "Muddat nazorati", ru: "Контроль срока" } as T,
      manual: { uz: "Excel yoki daftar, har kuni tekshirish kerak", ru: "Excel или блокнот, проверять нужно каждый день" } as T,
      getolog: { uz: "Har bir obunachining muddati tizimda saqlanadi", ru: "Срок каждого подписчика хранится в системе" } as T,
    },
    {
      label: { uz: "Eslatma yuborish", ru: "Напоминания" } as T,
      manual: { uz: "Yodda tutish va qo'lda yozish", ru: "Помнить и писать вручную" } as T,
      getolog: { uz: "Muddat tugashidan oldin avtomatik eslatma", ru: "Автоматическое напоминание перед окончанием" } as T,
    },
    {
      label: { uz: "Muddati tugaganini chiqarish", ru: "Удаление по истечении срока" } as T,
      manual: { uz: "Ko'pincha unutiladi — odam bepul qolib ketadi", ru: "Часто забывается — человек остаётся бесплатно" } as T,
      getolog: { uz: "Muddat tugagan kuni avtomatik chiqariladi", ru: "Удаляется автоматически в день окончания" } as T,
    },
    {
      label: { uz: "Hisobot", ru: "Отчётность" } as T,
      manual: { uz: "Qo'lda sanash", ru: "Ручной подсчёт" } as T,
      getolog: { uz: "Obunachi soni va tushum panelda ko'rinadi", ru: "Количество подписчиков и доход видны в панели" } as T,
    },
  ] as CompareRow[],
};

export const landingPages: LandingPage[] = [
  /* ─────────────────────────────────────────────────────────────
     1. Getolog nima — brend / entity sahifasi (AI GEO uchun asosiy)
     ───────────────────────────────────────────────────────────── */
  {
    slug: "getolog-nima",
    keyword: { uz: "Getolog nima", ru: "Что такое Getolog" },
    title: {
      uz: "Getolog nima va pullik Telegram kanallar uchun qanday ishlaydi?",
      ru: "Что такое Getolog и как он работает для платных Telegram-каналов?",
    },
    h1: {
      uz: "Getolog nima va u pullik Telegram kanallar uchun qanday ishlaydi?",
      ru: "Что такое Getolog и как он работает для платных Telegram-каналов?",
    },
    description: {
      uz: "Getolog — yopiq Telegram kanal va guruhlar uchun obuna avtomatlashtirish xizmati: to'lov, bir martalik invite-link, muddat nazorati va avtomatik chiqarish. To'lov to'g'ridan-to'g'ri kartangizga tushadi.",
      ru: "Getolog — сервис автоматизации подписок для закрытых Telegram-каналов и групп: оплата, одноразовая invite-ссылка, контроль срока и автоудаление. Оплата поступает напрямую на вашу карту.",
    },
    answer: {
      uz: "Getolog — yopiq Telegram kanal va guruhlar uchun obuna avtomatlashtirish xizmati. Siz BotFather'dan olingan bot tokeningizni berasiz, Getolog undan sotuvchi bot yasaydi: bot to'lovni qabul qiladi, bir martalik invite-link beradi, obuna muddatini kuzatadi va muddat tugagach foydalanuvchini kanaldan avtomatik chiqaradi. To'lov to'g'ridan-to'g'ri sizning kartangizga tushadi.",
      ru: "Getolog — сервис автоматизации подписок для закрытых Telegram-каналов и групп. Вы передаёте токен бота из BotFather, Getolog превращает его в бота-продавца: бот принимает оплату, выдаёт одноразовую invite-ссылку, следит за сроком подписки и автоматически удаляет пользователя из канала по её окончании. Оплата поступает напрямую на вашу карту.",
    },
    published: "2026-08-10",
    updated: "2026-08-10",
    category: { uz: "Xizmat haqida", ru: "О сервисе" },
    readTime: { uz: "6 daqiqa", ru: "6 минут" },
    sections: [
      {
        h2: { uz: "Getolog qanday ishlaydi?", ru: "Как работает Getolog?" },
        html: {
          uz: `<p>Getolog sizning o'rningizga bitta ishni bajaradi: <strong>pulni olgan odamni kanalga kiritish va muddati tugaganini chiqarish</strong>. Jarayon shunday ketadi:</p>
<ol>
<li><strong>Bot yaratasiz.</strong> Telegram'dagi <code>@BotFather</code> orqali o'z botingizni ochasiz va token olasiz. Bu 2 daqiqalik ish.</li>
<li><strong>Tokenni Getolog'ga berasiz.</strong> Getolog o'sha botni sotuvchi botga aylantiradi — bot sizning nomingiz va logotipingiz bilan ishlaydi.</li>
<li><strong>Tarif belgilaysiz.</strong> 1, 3, 6 yoki 12 oylik narxlarni o'zingiz kiritasiz.</li>
<li><strong>Obunachi to'laydi.</strong> Bot karta rekvizitini beradi, odam pul o'tkazadi va chek rasmini botga yuboradi.</li>
<li><strong>Siz tasdiqlaysiz.</strong> Panelda chek ko'rinadi — bir tugma bilan tasdiqlaysiz yoki rad etasiz.</li>
<li><strong>Bot kirish beradi.</strong> Tasdiqdan keyin bot <strong>bir martalik</strong> invite-link yuboradi. Link faqat bitta odamga ishlaydi.</li>
<li><strong>Muddat kuzatiladi.</strong> Tugashidan oldin eslatma yuboriladi, tugagan kuni odam kanaldan avtomatik chiqariladi.</li>
</ol>
<p>Siz faqat kontent joylaysiz. Qolgan hamma narsa — <a href="/telegram-obuna-bot">obuna botining</a> ishi.</p>`,
          ru: `<p>Getolog делает за вас одну работу: <strong>впускает в канал того, кто заплатил, и удаляет того, у кого срок истёк</strong>. Процесс выглядит так:</p>
<ol>
<li><strong>Создаёте бота.</strong> Через <code>@BotFather</code> в Telegram открываете своего бота и получаете токен. Это 2 минуты.</li>
<li><strong>Передаёте токен в Getolog.</strong> Getolog превращает этого бота в бота-продавца — он работает под вашим именем и логотипом.</li>
<li><strong>Задаёте тарифы.</strong> Цены на 1, 3, 6 и 12 месяцев вы устанавливаете сами.</li>
<li><strong>Подписчик оплачивает.</strong> Бот выдаёт реквизиты карты, человек переводит деньги и отправляет фото чека боту.</li>
<li><strong>Вы подтверждаете.</strong> Чек появляется в панели — подтверждаете или отклоняете одной кнопкой.</li>
<li><strong>Бот выдаёт доступ.</strong> После подтверждения бот отправляет <strong>одноразовую</strong> invite-ссылку. Она сработает только у одного человека.</li>
<li><strong>Срок отслеживается.</strong> Перед окончанием приходит напоминание, в день окончания человек автоматически удаляется из канала.</li>
</ol>
<p>Вы только публикуете контент. Всё остальное — работа <a href="/ru/telegram-obuna-bot">бота подписки</a>.</p>`,
        },
      },
      {
        h2: { uz: "Kimga mos?", ru: "Кому подходит?" },
        html: {
          uz: `<p>Getolog obunachilari doimiy ravishda yangilanib turadigan yopiq jamoalar uchun yozilgan:</p>
<ul>
<li><strong>O'qituvchi va repetitorlar</strong> — ingliz tili, matematika, IT kurslarining yopiq guruhlari.</li>
<li><strong>Onlayn kurs egalari</strong> — <a href="/blog/telegram-kanalni-pullik-qilish">kursni Telegram kanal orqali sotadiganlar</a>.</li>
<li><strong>Ekspert va blogerlar</strong> — pullik kontent, arxiv, yopiq maslahat kanallari.</li>
<li><strong>Klub va jamoa egalari</strong> — a'zolik to'lovi bilan ishlaydigan closed-community'lar.</li>
</ul>
<p>Agar kanalingizda 20 tadan ortiq pullik obunachi bo'lsa va ularning muddatlarini qo'lda kuzatayotgan bo'lsangiz — bu aynan siz uchun. 20 tagacha obunachi bepul tarifda ham yetadi.</p>`,
          ru: `<p>Getolog создан для закрытых сообществ, состав которых постоянно обновляется:</p>
<ul>
<li><strong>Преподаватели и репетиторы</strong> — закрытые группы курсов английского, математики, IT.</li>
<li><strong>Владельцы онлайн-курсов</strong> — те, кто <a href="/ru/blog/telegram-kanalni-pullik-qilish">продаёт курс через Telegram-канал</a>.</li>
<li><strong>Эксперты и блогеры</strong> — платный контент, архив, закрытые консультационные каналы.</li>
<li><strong>Владельцы клубов и сообществ</strong> — closed-community с членским взносом.</li>
</ul>
<p>Если у вас больше 20 платных подписчиков и вы ведёте их сроки вручную — это для вас. До 20 подписчиков хватает и бесплатного тарифа.</p>`,
        },
      },
      {
        h2: { uz: "Narxi qancha?", ru: "Сколько стоит?" },
        html: {
          uz: `<p>Getolog <strong>tushumingizdan komissiya olmaydi</strong>. To'lov obunachidan to'g'ridan-to'g'ri sizning kartangizga tushadi — Getolog pulga tegmaydi. Siz faqat oylik tarifni to'laysiz:</p>
<table>
<thead><tr><th>Tarif</th><th>Narxi (oyiga)</th><th>Faol obunachi</th></tr></thead>
<tbody>
<tr><td>Bepul</td><td>0 so'm</td><td>20 tagacha</td></tr>
<tr><td>Minimal</td><td>295 000 so'm</td><td>100 tagacha</td></tr>
<tr><td>Standart</td><td>590 000 so'm</td><td>200 tagacha</td></tr>
<tr><td>Pro</td><td>1 270 000 so'm</td><td>500 tagacha</td></tr>
<tr><td>Biznes</td><td>1 890 000 so'm</td><td>1000 tagacha</td></tr>
</tbody>
</table>
<p>Oddiy hisob: obuna narxingiz 100 000 so'm bo'lsa, Minimal tarif atigi 3 ta obunachining puliga teng. Qolgan 97 tasining puli to'liq sizda qoladi. Barcha imkoniyatlarning to'liq taqqoslanishi — <a href="/price">tariflar sahifasida</a>.</p>`,
          ru: `<p>Getolog <strong>не берёт комиссию с вашего дохода</strong>. Оплата поступает от подписчика напрямую на вашу карту — Getolog не касается денег. Вы платите только за месячный тариф:</p>
<table>
<thead><tr><th>Тариф</th><th>Цена (в месяц)</th><th>Активных подписчиков</th></tr></thead>
<tbody>
<tr><td>Бесплатный</td><td>0 сум</td><td>до 20</td></tr>
<tr><td>Минимал</td><td>295 000 сум</td><td>до 100</td></tr>
<tr><td>Стандарт</td><td>590 000 сум</td><td>до 200</td></tr>
<tr><td>Про</td><td>1 270 000 сум</td><td>до 500</td></tr>
<tr><td>Бизнес</td><td>1 890 000 сум</td><td>до 1000</td></tr>
</tbody>
</table>
<p>Простой расчёт: если ваша подписка стоит 100 000 сум, тариф «Минимал» равен деньгам всего трёх подписчиков. Доход от остальных 97 остаётся у вас полностью. Полное сравнение возможностей — на <a href="/ru/price">странице тарифов</a>.</p>`,
        },
      },
      {
        h2: { uz: "Nega o'z botingiz bo'lgani muhim?", ru: "Почему важно, чтобы бот был вашим?" },
        html: {
          uz: `<p>Getolog umumiy bot bermaydi — <strong>bot sizniki bo'lib qoladi</strong>. Token sizda, nom sizniki, obunachilar bazasi sizning botingizda. Bu uchta amaliy narsani anglatadi:</p>
<ul>
<li><strong>Ishonch.</strong> Obunachi begona xizmatga emas, sizning brendingizga pul to'laydi.</li>
<li><strong>Mustaqillik.</strong> Xohlagan vaqtda tokenni almashtirasiz — bot boshqaruvi baribir sizda qoladi.</li>
<li><strong>Xavfsizlik.</strong> Token shifrlangan holda saqlanadi va to'lov oqimiga umuman aralashmaydi.</li>
</ul>
<p>Bepul tarifda bot xabarlarida Getolog brendi ko'rsatiladi; pullik tariflarda u olib tashlanadi.</p>`,
          ru: `<p>Getolog не выдаёт общего бота — <strong>бот остаётся вашим</strong>. Токен у вас, имя ваше, база подписчиков — в вашем боте. Это даёт три практических вещи:</p>
<ul>
<li><strong>Доверие.</strong> Подписчик платит вашему бренду, а не постороннему сервису.</li>
<li><strong>Независимость.</strong> Вы в любой момент можете сменить токен — управление ботом всё равно остаётся у вас.</li>
<li><strong>Безопасность.</strong> Токен хранится в зашифрованном виде и вообще не участвует в денежном потоке.</li>
</ul>
<p>На бесплатном тарифе в сообщениях бота показывается брендинг Getolog; на платных он убирается.</p>`,
        },
      },
      {
        h2: { uz: "Qanday boshlanadi?", ru: "Как начать?" },
        html: {
          uz: `<p>Sozlash o'rtacha 2 daqiqa oladi va dasturlash talab qilmaydi:</p>
<ol>
<li><a href="https://t.me/getologbot" target="_blank" rel="noopener noreferrer">@getologbot</a> ga <code>/start</code> yuborasiz.</li>
<li><code>@BotFather</code> dan olingan tokeningizni kiritasiz.</li>
<li>Kanalingizni ulaysiz va botni administrator qilasiz.</li>
<li>Tarif narxlarini kiritasiz — bot sotuvga tayyor.</li>
</ol>
<p>Savol tug'ilsa yoki sozlashda yordam kerak bo'lsa — <a href="https://t.me/getolog_bot" target="_blank" rel="noopener noreferrer">@getolog_bot</a> support botiga yozing yoki <a href="/ariza">ariza qoldiring</a>, jamoamiz o'zi bog'lanadi.</p>`,
          ru: `<p>Настройка занимает в среднем 2 минуты и не требует программирования:</p>
<ol>
<li>Отправьте <code>/start</code> боту <a href="https://t.me/getologbot" target="_blank" rel="noopener noreferrer">@getologbot</a>.</li>
<li>Введите токен, полученный у <code>@BotFather</code>.</li>
<li>Подключите канал и сделайте бота администратором.</li>
<li>Укажите цены тарифов — бот готов к продажам.</li>
</ol>
<p>Если появятся вопросы или нужна помощь с настройкой — напишите в support-бот <a href="https://t.me/getolog_bot" target="_blank" rel="noopener noreferrer">@getolog_bot</a> или <a href="/ru/ariza">оставьте заявку</a>, команда свяжется сама.</p>`,
        },
      },
    ],
    compare: compareCommon,
    faq: [
      {
        q: { uz: "Getolog to'lovdan komissiya oladimi?", ru: "Берёт ли Getolog комиссию с оплаты?" },
        a: {
          uz: "Yo'q. Obunachining puli to'g'ridan-to'g'ri sizning kartangizga tushadi, Getolog to'lov oqimiga umuman aralashmaydi. Siz faqat oylik tarif to'laysiz — tushumdan foiz olinmaydi.",
          ru: "Нет. Деньги подписчика поступают напрямую на вашу карту, Getolog вообще не участвует в денежном потоке. Вы платите только месячный тариф — процент с дохода не берётся.",
        },
      },
      {
        q: { uz: "Pullik kanal ochish uchun dasturlashni bilish kerakmi?", ru: "Нужно ли уметь программировать, чтобы открыть платный канал?" },
        a: {
          uz: "Yo'q. Kod yozilmaydi. BotFather'dan token olib, uni Getolog'ga kiritasiz — qolgan sozlash tugmalar orqali qilinadi.",
          ru: "Нет. Код писать не нужно. Вы получаете токен у BotFather и вводите его в Getolog — остальная настройка делается кнопками.",
        },
      },
      {
        q: { uz: "Getolog guruhlar bilan ham ishlaydimi?", ru: "Работает ли Getolog с группами?" },
        a: {
          uz: "Ha. Yopiq Telegram guruhlar ham qo'llab-quvvatlanadi — kirish, muddat nazorati va chiqarish kanaldagidek ishlaydi.",
          ru: "Да. Закрытые Telegram-группы тоже поддерживаются — вход, контроль срока и удаление работают так же, как в канале.",
        },
      },
      {
        q: { uz: "Bot tokenim xavfsizmi?", ru: "Безопасен ли мой токен бота?" },
        a: {
          uz: "Token shifrlangan holda saqlanadi va xohlagan vaqtda almashtirilishi mumkin. Token faqat botni boshqarish uchun ishlatiladi, to'lov ma'lumotlariga aloqasi yo'q.",
          ru: "Токен хранится в зашифрованном виде и может быть заменён в любой момент. Он используется только для управления ботом и не связан с платёжными данными.",
        },
      },
      {
        q: { uz: "Bepul tarifda nima cheklangan?", ru: "Что ограничено на бесплатном тарифе?" },
        a: {
          uz: "Bepul tarifda 20 tagacha faol obunachi bo'lishi mumkin va bot xabarlarida Getolog brendi ko'rsatiladi. Qolgan asosiy funksiyalar — to'lov, bir martalik link, muddat nazorati — ishlaydi.",
          ru: "На бесплатном тарифе допускается до 20 активных подписчиков, а в сообщениях бота показывается брендинг Getolog. Остальные основные функции — оплата, одноразовая ссылка, контроль срока — работают.",
        },
      },
      {
        q: { uz: "Getolog qaysi mamlakatda ishlaydi?", ru: "В какой стране работает Getolog?" },
        a: {
          uz: "Getolog O'zbekiston bozori uchun yozilgan: narxlar so'mda, to'lov Uzcard/Humo kartalari orqali, interfeys o'zbek va rus tillarida.",
          ru: "Getolog создан для рынка Узбекистана: цены в сумах, оплата через карты Uzcard/Humo, интерфейс на узбекском и русском языках.",
        },
      },
    ],
    related: ["telegram-obuna-bot", "telegram-kanalga-tolov-qabul-qilish", "obuna-tugaganda-kanaldan-chiqarish"],
    relatedArticles: ["telegram-kanalni-pullik-qilish", "obuna-bot-sozlash"],
  },

  /* ─────────────────────────────────────────────────────────────
     2. Telegram obuna bot
     ───────────────────────────────────────────────────────────── */
  {
    slug: "telegram-obuna-bot",
    keyword: { uz: "telegram obuna bot", ru: "телеграм бот подписки" },
    title: {
      uz: "Telegram obuna bot: to'lovdan avtomatik kirishgacha (2026)",
      ru: "Telegram-бот подписки: от оплаты до автоматического входа (2026)",
    },
    h1: {
      uz: "Telegram obuna bot: to'lovdan avtomatik kirishgacha",
      ru: "Telegram-бот подписки: от оплаты до автоматического входа",
    },
    description: {
      uz: "Telegram obuna bot nima qiladi, qanday yaratiladi va to'lovdan kanalga kirishgacha bo'lgan jarayon qanday ishlaydi — O'zbekiston uchun amaliy qo'llanma.",
      ru: "Что делает Telegram-бот подписки, как его создать и как устроен путь от оплаты до входа в канал — практическое руководство для Узбекистана.",
    },
    answer: {
      uz: "Telegram obuna bot — yopiq kanalga pullik kirishni boshqaradigan bot. U tarifni ko'rsatadi, to'lovni qabul qiladi, chekni tasdiqlatadi, bir martalik invite-link beradi, obuna muddatini saqlaydi, tugashidan oldin eslatma yuboradi va muddat tugagach foydalanuvchini kanaldan chiqaradi. Botni BotFather orqali 2 daqiqada yaratib, Getolog'ga ulash mumkin.",
      ru: "Telegram-бот подписки — это бот, который управляет платным доступом в закрытый канал. Он показывает тарифы, принимает оплату, проводит подтверждение чека, выдаёт одноразовую invite-ссылку, хранит срок подписки, напоминает о продлении и удаляет пользователя из канала по истечении срока. Бота можно создать в BotFather за 2 минуты и подключить к Getolog.",
    },
    published: "2026-08-10",
    updated: "2026-08-10",
    category: { uz: "Yo'riqnoma", ru: "Инструкция" },
    readTime: { uz: "7 daqiqa", ru: "7 минут" },
    sections: [
      {
        h2: { uz: "Telegram obuna bot aslida nima qiladi?", ru: "Что на самом деле делает бот подписки?" },
        html: {
          uz: `<p>Ko'pchilik "obuna bot" deganda faqat to'lov qabul qilishni tushunadi. Aslida ish to'lovdan keyin boshlanadi. To'liq ro'yxat:</p>
<ul>
<li><strong>Tarifni ko'rsatadi</strong> — 1, 3, 6, 12 oylik narxlar tugmalar ko'rinishida.</li>
<li><strong>To'lov rekvizitini beradi</strong> — karta raqami va aniq summa.</li>
<li><strong>Chekni qabul qiladi</strong> — obunachi to'lov skrinshotini yuboradi.</li>
<li><strong>Tasdiqlashga yuboradi</strong> — siz yoki moderatoringiz panelda ko'rib tasdiqlaydi.</li>
<li><strong>Bir martalik havola beradi</strong> — <a href="/obuna-tugaganda-kanaldan-chiqarish">faqat bitta odam</a> kira oladigan link.</li>
<li><strong>Muddatni saqlaydi</strong> — kim qachongacha to'lagan, hammasi bazada.</li>
<li><strong>Eslatma yuboradi</strong> — muddat tugashiga bir necha kun qolganda.</li>
<li><strong>Chiqaradi</strong> — muddat tugagan kuni avtomatik.</li>
</ul>
<p>Ya'ni obuna bot — bu "to'lov boti" emas, <strong>kirish nazorati tizimi</strong>.</p>`,
          ru: `<p>Многие под «ботом подписки» понимают только приём оплаты. На деле работа начинается после оплаты. Полный список:</p>
<ul>
<li><strong>Показывает тарифы</strong> — цены на 1, 3, 6, 12 месяцев в виде кнопок.</li>
<li><strong>Выдаёт реквизиты</strong> — номер карты и точную сумму.</li>
<li><strong>Принимает чек</strong> — подписчик отправляет скриншот оплаты.</li>
<li><strong>Отправляет на подтверждение</strong> — вы или ваш модератор подтверждаете в панели.</li>
<li><strong>Выдаёт одноразовую ссылку</strong> — по ней сможет войти <a href="/ru/obuna-tugaganda-kanaldan-chiqarish">только один человек</a>.</li>
<li><strong>Хранит срок</strong> — кто до какого числа оплатил, всё в базе.</li>
<li><strong>Напоминает</strong> — за несколько дней до окончания.</li>
<li><strong>Удаляет</strong> — автоматически в день окончания.</li>
</ul>
<p>То есть бот подписки — это не «бот для оплаты», а <strong>система контроля доступа</strong>.</p>`,
        },
      },
      {
        h2: { uz: "Botni qanday yaratish mumkin? 5 qadam", ru: "Как создать бота? 5 шагов" },
        html: {
          uz: `<ol>
<li><strong>BotFather'ni oching.</strong> Telegram qidiruvidan <code>@BotFather</code> ni toping va <code>/newbot</code> yuboring.</li>
<li><strong>Nom va username bering.</strong> Username <code>bot</code> bilan tugashi shart, masalan <code>ingliz_premium_bot</code>.</li>
<li><strong>Tokenni saqlang.</strong> BotFather uzun bir qator beradi — bu sizning kalitingiz, hech kimga bermang.</li>
<li><strong>Tokenni Getolog'ga kiriting.</strong> <a href="https://t.me/getologbot" target="_blank" rel="noopener noreferrer">@getologbot</a> ga kirib tokenni yuboring — bot bir necha soniyada sotuvchi botga aylanadi.</li>
<li><strong>Kanalni ulang.</strong> Botni kanalingizga administrator qiling va "invite link yaratish" huquqini bering. Shu bilan sozlash tugadi.</li>
</ol>
<p>Bu jarayonda kod yozilmaydi va server sotib olinmaydi. Batafsil bosqichma-bosqich yo'riqnoma — <a href="/blog/obuna-bot-sozlash">obuna bot sozlash maqolasida</a>.</p>`,
          ru: `<ol>
<li><strong>Откройте BotFather.</strong> Найдите в поиске Telegram <code>@BotFather</code> и отправьте <code>/newbot</code>.</li>
<li><strong>Задайте имя и username.</strong> Username обязан заканчиваться на <code>bot</code>, например <code>english_premium_bot</code>.</li>
<li><strong>Сохраните токен.</strong> BotFather выдаст длинную строку — это ваш ключ, никому его не передавайте.</li>
<li><strong>Введите токен в Getolog.</strong> Зайдите в <a href="https://t.me/getologbot" target="_blank" rel="noopener noreferrer">@getologbot</a> и отправьте токен — за несколько секунд бот станет ботом-продавцом.</li>
<li><strong>Подключите канал.</strong> Сделайте бота администратором канала и дайте право создавать invite-ссылки. На этом настройка закончена.</li>
</ol>
<p>В этом процессе не пишется код и не покупается сервер. Подробная пошаговая инструкция — в статье <a href="/ru/blog/obuna-bot-sozlash">о настройке бота подписки</a>.</p>`,
        },
      },
      {
        h2: { uz: "To'lovdan kirishgacha bo'lgan yo'l", ru: "Путь от оплаты до входа" },
        html: {
          uz: `<p>Obunachi tomondan bu jarayon shunday ko'rinadi — hammasi Telegram ichida, sayt ham, ro'yxatdan o'tish ham yo'q:</p>
<ol>
<li>Odam bot havolasini bosadi va <code>/start</code> yuboradi.</li>
<li>Bot kanal haqida qisqa ma'lumot va tariflarni ko'rsatadi.</li>
<li>Odam "3 oy — 270 000 so'm" tugmasini bosadi.</li>
<li>Bot karta raqami va aniq summani yuboradi.</li>
<li>Odam pul o'tkazadi va chek rasmini shu yerga tashlaydi.</li>
<li>Siz panelda tasdiqlaysiz (o'rtacha bir necha daqiqa).</li>
<li>Bot bir martalik havolani yuboradi, odam kanalga kiradi.</li>
</ol>
<p>Muhimi: havola ishlatilgandan keyin o'ladi. Uni do'stiga yuborsa ham, ikkinchi odam kira olmaydi — <a href="/blog/invite-link-xavfsizligi">invite-link xavfsizligi</a> aynan shu yerda ishlaydi.</p>`,
          ru: `<p>Со стороны подписчика это выглядит так — всё внутри Telegram, без сайта и регистрации:</p>
<ol>
<li>Человек переходит по ссылке на бота и отправляет <code>/start</code>.</li>
<li>Бот показывает краткую информацию о канале и тарифы.</li>
<li>Человек нажимает «3 месяца — 270 000 сум».</li>
<li>Бот присылает номер карты и точную сумму.</li>
<li>Человек переводит деньги и отправляет фото чека сюда же.</li>
<li>Вы подтверждаете в панели (в среднем за несколько минут).</li>
<li>Бот отправляет одноразовую ссылку, человек входит в канал.</li>
</ol>
<p>Важно: после использования ссылка «умирает». Даже если её перешлют другу, второй человек войти не сможет — здесь и работает <a href="/ru/blog/invite-link-xavfsizligi">защита invite-ссылок</a>.</p>`,
        },
      },
      {
        h2: { uz: "Kimga kerak va qachondan kerak bo'ladi?", ru: "Кому и с какого момента это нужно?" },
        html: {
          uz: `<p>Oddiy mezon — obunachilar soni va muddatlar soni. Taxminiy hisob:</p>
<ul>
<li><strong>10 tagacha obunachi:</strong> qo'lda ham bardosh berish mumkin, lekin har oy 10 ta muddatni eslab qolish kerak.</li>
<li><strong>30–50 obunachi:</strong> har kuni kimningdir muddati tugaydi. Excel bilan boshqarish kuniga 20–30 daqiqa oladi.</li>
<li><strong>100+ obunachi:</strong> qo'lda boshqarish real emas — bir nechta odam har oy bepul qolib ketadi.</li>
</ul>
<p>Yo'qotishni hisoblab ko'ring: obuna 100 000 so'm bo'lsa va oyiga atigi 5 ta odam "unutilgan" holda bepul qolsa, bu 500 000 so'm — Standart tarifning narxidan ham ko'p.</p>`,
          ru: `<p>Простой критерий — количество подписчиков и количество сроков. Примерный расчёт:</p>
<ul>
<li><strong>До 10 подписчиков:</strong> можно и вручную, но каждый месяц нужно помнить 10 дат.</li>
<li><strong>30–50 подписчиков:</strong> срок истекает у кого-то почти каждый день. Ведение в Excel отнимает 20–30 минут в день.</li>
<li><strong>100+ подписчиков:</strong> ручное управление нереально — каждый месяц кто-то остаётся бесплатно.</li>
</ul>
<p>Посчитайте потери: если подписка стоит 100 000 сум и всего 5 человек в месяц «забыты» и сидят бесплатно, это 500 000 сум — больше стоимости тарифа «Стандарт».</p>`,
        },
      },
      {
        h2: { uz: "Narxi qancha?", ru: "Сколько стоит?" },
        html: {
          uz: `<p>Getolog'da obuna boti tushumdan foiz olmaydi — oylik tarif to'lanadi. Bepul tarif 20 tagacha obunachi uchun, keyin Minimal (295 000 so'm), Standart (590 000 so'm), Pro (1 270 000 so'm) va Biznes (1 890 000 so'm) tariflari bor.</p>
<p>Botni yozdirish (dasturchi buyurtmasi) odatda 3–10 million so'm turadi va keyin har oy server hamda texnik xizmat to'lanadi. Tayyor yechim shu sababli aksariyat o'qituvchi va kurs egalari uchun tezroq va arzonroq chiqadi. Barcha tariflar taqqoslanishi — <a href="/price">tariflar sahifasida</a>.</p>`,
          ru: `<p>В Getolog бот подписки не берёт процент с дохода — оплачивается месячный тариф. Бесплатный тариф рассчитан до 20 подписчиков, далее — «Минимал» (295 000 сум), «Стандарт» (590 000 сум), «Про» (1 270 000 сум) и «Бизнес» (1 890 000 сум).</p>
<p>Заказная разработка бота обычно стоит 3–10 млн сум, плюс ежемесячно сервер и техподдержка. Поэтому готовое решение для большинства преподавателей и владельцев курсов выходит быстрее и дешевле. Сравнение всех тарифов — на <a href="/ru/price">странице тарифов</a>.</p>`,
        },
      },
    ],
    compare: compareCommon,
    faq: [
      {
        q: { uz: "Pullik Telegram kanal uchun qaysi bot kerak?", ru: "Какой бот нужен для платного Telegram-канала?" },
        a: {
          uz: "Sizga to'lovni qabul qilish bilan birga kirish nazoratini ham bajaradigan bot kerak: bir martalik invite-link berish, obuna muddatini saqlash va muddat tugaganda kanaldan chiqarish. Faqat to'lov qabul qiladigan bot muammoni yarmini ham yechmaydi.",
          ru: "Нужен бот, который вместе с приёмом оплаты выполняет и контроль доступа: выдаёт одноразовую invite-ссылку, хранит срок подписки и удаляет из канала по его окончании. Бот, который только принимает оплату, не решает и половины задачи.",
        },
      },
      {
        q: { uz: "Bot tayyor bo'lishi uchun qancha vaqt ketadi?", ru: "Сколько времени занимает запуск бота?" },
        a: {
          uz: "BotFather'da bot yaratish 2 daqiqa, tokenni Getolog'ga ulash va tariflarni kiritish yana bir necha daqiqa. Odatda 10 daqiqa ichida bot sotuvga tayyor bo'ladi.",
          ru: "Создание бота в BotFather — 2 минуты, подключение токена к Getolog и ввод тарифов — ещё несколько минут. Обычно бот готов к продажам за 10 минут.",
        },
      },
      {
        q: { uz: "Bitta bot bir nechta kanalga xizmat qila oladimi?", ru: "Может ли один бот обслуживать несколько каналов?" },
        a: {
          uz: "Ha. Tarifingizga qarab bir nechta kanal yoki guruhni bitta hisobga ulash mumkin — har biriga alohida tarif va narx belgilanadi.",
          ru: "Да. В зависимости от тарифа к одному аккаунту можно подключить несколько каналов или групп — для каждого задаются свои тарифы и цены.",
        },
      },
      {
        q: { uz: "Obunachi to'lovni tunda qilsa, kirishni kutib turadimi?", ru: "Если подписчик платит ночью, будет ли он ждать доступ?" },
        a: {
          uz: "Chek tasdiqlanishi sizga yoki moderatoringizga bog'liq. Shu sababli katta kanallarda moderator qo'shish tavsiya qilinadi — bot tasdiqdan keyin havolani darhol o'zi yuboradi.",
          ru: "Подтверждение чека зависит от вас или вашего модератора. Поэтому в крупных каналах рекомендуется добавить модератора — после подтверждения бот отправляет ссылку сам и мгновенно.",
        },
      },
      {
        q: { uz: "Bot obunachilar bazasini kimga tegishli qiladi?", ru: "Кому принадлежит база подписчиков бота?" },
        a: {
          uz: "Bot sizniki, token sizda, obunachilar ham sizning botingizda. Getolog xizmatidan chiqsangiz ham bot va uning obunachilari sizda qoladi.",
          ru: "Бот ваш, токен у вас, подписчики — в вашем боте. Даже если вы уйдёте из сервиса, бот и его подписчики останутся у вас.",
        },
      },
      {
        q: { uz: "Bot ishlamay qolsa obunachilar kanaldan chiqib ketadimi?", ru: "Если бот перестанет работать, подписчики выйдут из канала?" },
        a: {
          uz: "Yo'q. Kanaldagi mavjud a'zolar joyida qoladi — bot faqat yangi kirish berish va muddati tugaganini chiqarish uchun ishlaydi.",
          ru: "Нет. Уже состоящие в канале участники остаются на месте — бот отвечает только за выдачу нового доступа и удаление по истечении срока.",
        },
      },
    ],
    related: ["getolog-nima", "telegram-kanalga-tolov-qabul-qilish", "obuna-tugaganda-kanaldan-chiqarish"],
    relatedArticles: ["obuna-bot-sozlash", "invite-link-xavfsizligi"],
  },

  /* ─────────────────────────────────────────────────────────────
     3. Telegram kanalga to'lov qabul qilish
     ───────────────────────────────────────────────────────────── */
  {
    slug: "telegram-kanalga-tolov-qabul-qilish",
    keyword: { uz: "telegram kanalga to'lov qabul qilish", ru: "приём оплаты в Telegram-канале" },
    title: {
      uz: "Telegram kanalga to'lov qabul qilish: karta, Payme va Click",
      ru: "Приём оплаты в Telegram-канале: карта, Payme и Click",
    },
    h1: {
      uz: "Telegram kanalda Payme, Click va karta orqali to'lov olish",
      ru: "Приём оплаты в Telegram-канале через Payme, Click и карту",
    },
    description: {
      uz: "Telegram kanalga to'lov qabul qilishning uchta yo'li: karta o'tkazmasi + chek tasdiqlash, Payme/Click merchant va Telegram Stars. Qaysi biri kimga mos — solishtirib chiqamiz.",
      ru: "Три способа принимать оплату в Telegram-канале: перевод на карту с подтверждением чека, мерчант Payme/Click и Telegram Stars. Разбираем, кому какой подходит.",
    },
    answer: {
      uz: "Telegram kanalga to'lov qabul qilishning uchta amaliy yo'li bor: karta o'tkazmasi va chekni bot orqali tasdiqlash, Payme yoki Click merchant hisobini ulash, hamda Telegram Stars. O'zbekistondagi aksariyat o'qituvchi va kurs egalari uchun eng tez yo'l — karta o'tkazmasi, chunki u yuridik shaxs va merchant shartnomasini talab qilmaydi.",
      ru: "Есть три рабочих способа принимать оплату в Telegram-канале: перевод на карту с подтверждением чека через бота, подключение мерчанта Payme или Click и Telegram Stars. Для большинства преподавателей и владельцев курсов в Узбекистане быстрее всего перевод на карту — он не требует юрлица и договора с мерчантом.",
    },
    published: "2026-08-10",
    updated: "2026-08-10",
    category: { uz: "To'lovlar", ru: "Платежи" },
    readTime: { uz: "7 daqiqa", ru: "7 минут" },
    sections: [
      {
        h2: { uz: "Qanday to'lov usullari mavjud?", ru: "Какие способы оплаты существуют?" },
        html: {
          uz: `<p>O'zbekistonda Telegram kanal uchun uchta real variant ishlaydi:</p>
<ol>
<li><strong>Karta o'tkazmasi + chek tasdiqlash.</strong> Bot Uzcard yoki Humo karta raqamini beradi, obunachi pul o'tkazadi va chek rasmini yuboradi, siz tasdiqlaysiz. Hech qanday shartnoma kerak emas.</li>
<li><strong>Payme / Click merchant.</strong> To'lov avtomatik tasdiqlanadi, lekin buning uchun YaTT yoki MChJ, shartnoma va komissiya kerak. <a href="/payme-click-telegram-bot">Talablar va jarayon alohida sahifada</a>.</li>
<li><strong>Telegram Stars.</strong> Telegram'ning ichki valyutasi. Xalqaro auditoriya uchun qulay, lekin mahalliy karta bilan to'lovga qaraganda konversiyasi past va Telegram komissiyasi bor.</li>
</ol>`,
          ru: `<p>В Узбекистане для Telegram-канала реально работают три варианта:</p>
<ol>
<li><strong>Перевод на карту + подтверждение чека.</strong> Бот выдаёт номер карты Uzcard или Humo, подписчик переводит деньги и присылает фото чека, вы подтверждаете. Никаких договоров не нужно.</li>
<li><strong>Мерчант Payme / Click.</strong> Оплата подтверждается автоматически, но требуются ИП или ООО, договор и комиссия. <a href="/ru/payme-click-telegram-bot">Требования и процесс — на отдельной странице</a>.</li>
<li><strong>Telegram Stars.</strong> Внутренняя валюта Telegram. Удобна для международной аудитории, но конверсия ниже, чем при оплате местной картой, и есть комиссия Telegram.</li>
</ol>`,
        },
      },
      {
        h2: { uz: "Karta o'tkazmasi + chek tasdiqlash qanday ishlaydi?", ru: "Как работает перевод на карту с подтверждением чека?" },
        html: {
          uz: `<p>Bu O'zbekistonda eng ko'p ishlatiladigan model. Getolog'da jarayon shunday:</p>
<ol>
<li>Obunachi botda tarifni tanlaydi (masalan, 3 oy — 270 000 so'm).</li>
<li>Bot karta raqami va <strong>aniq summa</strong>ni yuboradi.</li>
<li>Odam bank ilovasi orqali o'tkazma qiladi va chek skrinshotini botga tashlaydi.</li>
<li>Chek sizning panelingizga tushadi: kim, qaysi tarif, qancha summa — hammasi ko'rinib turadi.</li>
<li>Siz "Tasdiqlash" tugmasini bosasiz — bot bir martalik havolani darhol yuboradi.</li>
</ol>
<p>Asosiy afzalligi: <strong>pul birinchi kundanoq to'g'ridan-to'g'ri sizning kartangizga tushadi</strong>, oradagi hech qanday hisob yo'q va komissiya olinmaydi.</p>`,
          ru: `<p>Это самая распространённая в Узбекистане модель. В Getolog процесс такой:</p>
<ol>
<li>Подписчик выбирает в боте тариф (например, 3 месяца — 270 000 сум).</li>
<li>Бот отправляет номер карты и <strong>точную сумму</strong>.</li>
<li>Человек делает перевод в банковском приложении и присылает боту скриншот чека.</li>
<li>Чек попадает в вашу панель: кто, какой тариф, какая сумма — всё видно.</li>
<li>Вы нажимаете «Подтвердить» — бот сразу отправляет одноразовую ссылку.</li>
</ol>
<p>Главное преимущество: <strong>деньги с первого же дня поступают напрямую на вашу карту</strong>, без промежуточных счетов и без комиссии.</p>`,
        },
      },
      {
        h2: { uz: "Qaysi usul kimga mos?", ru: "Кому какой способ подходит?" },
        html: {
          uz: `<table>
<thead><tr><th>Usul</th><th>Kimga mos</th><th>Talab</th><th>Tasdiqlash</th></tr></thead>
<tbody>
<tr><td>Karta + chek</td><td>O'qituvchi, repetitor, kichik kurs</td><td>Faqat karta</td><td>Qo'lda (bir tugma)</td></tr>
<tr><td>Payme / Click</td><td>YaTT / MChJ, katta oqim</td><td>Shartnoma, komissiya</td><td>Avtomatik</td></tr>
<tr><td>Telegram Stars</td><td>Xalqaro auditoriya</td><td>Telegram hisobi</td><td>Avtomatik</td></tr>
</tbody>
</table>
<p>Amaliy tavsiya: <strong>karta + chek</strong> bilan boshlang. Oyiga 100 dan ortiq to'lov bo'lgandan keyin qo'lda tasdiqlash og'irlik qila boshlaydi — o'shanda merchant ulashni ko'rib chiqing.</p>`,
          ru: `<table>
<thead><tr><th>Способ</th><th>Кому подходит</th><th>Требования</th><th>Подтверждение</th></tr></thead>
<tbody>
<tr><td>Карта + чек</td><td>Преподаватель, репетитор, небольшой курс</td><td>Только карта</td><td>Вручную (одна кнопка)</td></tr>
<tr><td>Payme / Click</td><td>ИП / ООО, большой поток</td><td>Договор, комиссия</td><td>Автоматически</td></tr>
<tr><td>Telegram Stars</td><td>Международная аудитория</td><td>Аккаунт Telegram</td><td>Автоматически</td></tr>
</tbody>
</table>
<p>Практический совет: начинайте с <strong>карты + чека</strong>. Когда платежей станет больше 100 в месяц, ручное подтверждение начнёт мешать — тогда и стоит рассмотреть мерчанта.</p>`,
        },
      },
      {
        h2: { uz: "To'lovni qanday xavfsiz qilish kerak?", ru: "Как сделать приём оплаты безопасным?" },
        html: {
          uz: `<p>Chek bilan ishlashda ikki xil xavf bor: soxta chek va "to'ladim" deb yozib, aslida to'lamaslik. Ularni oddiy qoidalar bilan yopish mumkin:</p>
<ul>
<li><strong>Aniq summa qoidasi.</strong> Har bir tarifga aniq summa biriktiring — mos kelmagan o'tkazmani tasdiqlamang.</li>
<li><strong>Chek panelda saqlanadi.</strong> Getolog har bir tasdiqlangan to'lovni tarixda saqlaydi, keyin bahs chiqsa dalil bor.</li>
<li><strong>Kirish faqat tasdiqdan keyin.</strong> Bot havolani hech qachon tasdiqdan oldin bermaydi.</li>
<li><strong>Havola bir martalik.</strong> Hatto to'lagan odam ham havolani boshqaga bera olmaydi.</li>
</ul>
<p>Aynan shu oxirgi nuqta pullik kanallarda eng ko'p pul yo'qotiladigan joy — <a href="/blog/invite-link-xavfsizligi">invite-link xavfsizligi</a> haqida alohida maqola bor.</p>`,
          ru: `<p>При работе с чеками есть два риска: поддельный чек и «я оплатил», хотя оплаты не было. Их закрывают простые правила:</p>
<ul>
<li><strong>Правило точной суммы.</strong> Привяжите к каждому тарифу точную сумму — не подтверждайте перевод, который не совпадает.</li>
<li><strong>Чек хранится в панели.</strong> Getolog сохраняет каждый подтверждённый платёж в истории — если возникнет спор, доказательство есть.</li>
<li><strong>Доступ только после подтверждения.</strong> Бот никогда не выдаёт ссылку до подтверждения.</li>
<li><strong>Ссылка одноразовая.</strong> Даже оплативший человек не сможет передать её другому.</li>
</ul>
<p>Именно последний пункт — место, где платные каналы теряют больше всего денег; об этом есть отдельная статья про <a href="/ru/blog/invite-link-xavfsizligi">безопасность invite-ссылок</a>.</p>`,
        },
      },
      {
        h2: { uz: "Komissiya va haqiqiy tannarx", ru: "Комиссия и реальная себестоимость" },
        html: {
          uz: `<p>Solishtirib ko'ramiz. Oyiga 100 ta obunachi, har biri 100 000 so'm to'laydi — jami 10 000 000 so'm.</p>
<ul>
<li><strong>Karta + Getolog Minimal:</strong> komissiya 0, tarif 295 000 so'm. Sizda qoladi ≈ 9 705 000 so'm.</li>
<li><strong>Merchant (o'rtacha komissiya bilan):</strong> tushumdan foiz olinadi, ustiga hisob-kitob va soliq hujjatlari qo'shiladi.</li>
</ul>
<p>Kichik va o'rta kanallar uchun karta modeli deyarli har doim foydaliroq chiqadi. Obuna narxini belgilash masalasi ham shu hisobga bog'liq — bu haqda <a href="/blog/pullik-kanal-uchun-maslahatlar">pullik kanal maslahatlarida</a> yozganmiz.</p>`,
          ru: `<p>Сравним. 100 подписчиков в месяц, каждый платит 100 000 сум — итого 10 000 000 сум.</p>
<ul>
<li><strong>Карта + Getolog «Минимал»:</strong> комиссия 0, тариф 295 000 сум. У вас остаётся ≈ 9 705 000 сум.</li>
<li><strong>Мерчант (со средней комиссией):</strong> удерживается процент с оборота, плюс добавляются бухгалтерия и налоговые документы.</li>
</ul>
<p>Для малых и средних каналов карточная модель почти всегда выгоднее. С этим же расчётом связан вопрос цены подписки — об этом мы писали в <a href="/ru/blog/pullik-kanal-uchun-maslahatlar">советах по ведению платного канала</a>.</p>`,
        },
      },
    ],
    compare: compareCommon,
    faq: [
      {
        q: { uz: "Telegram kanalga Payme yoki Click qanday ulanadi?", ru: "Как подключить Payme или Click к Telegram-каналу?" },
        a: {
          uz: "Payme yoki Click'ni ulash uchun merchant hisobi kerak: YaTT yoki MChJ, shartnoma va texnik integratsiya. Jarayon va talablar Payme/Click Telegram bot sahifasida batafsil yozilgan.",
          ru: "Для подключения Payme или Click нужен мерчант-аккаунт: ИП или ООО, договор и техническая интеграция. Процесс и требования подробно описаны на странице о Payme/Click для Telegram-бота.",
        },
      },
      {
        q: { uz: "Merchant hisobisiz to'lov olsa bo'ladimi?", ru: "Можно ли принимать оплату без мерчанта?" },
        a: {
          uz: "Ha. Karta o'tkazmasi va chekni bot orqali tasdiqlash usuli hech qanday merchant shartnomasini talab qilmaydi — jismoniy shaxs kartasi yetarli.",
          ru: "Да. Способ с переводом на карту и подтверждением чека через бота не требует договора с мерчантом — достаточно карты физического лица.",
        },
      },
      {
        q: { uz: "To'lov qilgan odam kanalga qanday avtomatik qo'shiladi?", ru: "Как оплативший человек автоматически попадает в канал?" },
        a: {
          uz: "To'lov tasdiqlangan zahoti bot foydalanuvchiga bir martalik invite-link yuboradi. Odam shu havola orqali kiradi va uning obuna muddati tizimda ochiladi.",
          ru: "Сразу после подтверждения оплаты бот отправляет пользователю одноразовую invite-ссылку. Человек входит по ней, и в системе открывается срок его подписки.",
        },
      },
      {
        q: { uz: "Chekni tekshirishga qancha vaqt ketadi?", ru: "Сколько времени занимает проверка чека?" },
        a: {
          uz: "Bir chekni ko'rib tasdiqlash bir necha soniya oladi — panelda summa, tarif va foydalanuvchi ko'rinib turadi. Ko'p oqimda moderator qo'shish mumkin.",
          ru: "Проверка одного чека занимает несколько секунд — в панели видны сумма, тариф и пользователь. При большом потоке можно добавить модератора.",
        },
      },
      {
        q: { uz: "Getolog to'lovni o'z hisobiga oladimi?", ru: "Получает ли Getolog оплату на свой счёт?" },
        a: {
          uz: "Yo'q. Pul obunachidan to'g'ridan-to'g'ri kanal egasining kartasiga o'tadi. Getolog to'lov oqimida qatnashmaydi va tushumdan foiz olmaydi.",
          ru: "Нет. Деньги идут от подписчика напрямую на карту владельца канала. Getolog не участвует в платёжном потоке и не берёт процент с дохода.",
        },
      },
      {
        q: { uz: "Telegram Stars mahalliy kanal uchun mos keladimi?", ru: "Подходят ли Telegram Stars для локального канала?" },
        a: {
          uz: "O'zbekistondagi auditoriya uchun odatda karta o'tkazmasi qulayroq: odamlar Uzcard/Humo bilan to'lashga o'rgangan. Stars ko'proq xalqaro obunachilar bo'lganda mantiqli.",
          ru: "Для аудитории в Узбекистане обычно удобнее перевод на карту: люди привыкли платить Uzcard/Humo. Stars имеют смысл, когда много международных подписчиков.",
        },
      },
    ],
    related: ["payme-click-telegram-bot", "telegram-obuna-bot", "getolog-nima"],
    relatedArticles: ["telegram-kanalni-pullik-qilish", "invite-link-xavfsizligi"],
  },

  /* ─────────────────────────────────────────────────────────────
     4. Payme / Click Telegram bot
     ───────────────────────────────────────────────────────────── */
  {
    slug: "payme-click-telegram-bot",
    keyword: { uz: "Payme Click Telegram bot", ru: "Payme Click Telegram бот" },
    title: {
      uz: "Telegram botga Payme va Click ulash: talablar, narx va jarayon",
      ru: "Подключение Payme и Click к Telegram-боту: требования, цена и процесс",
    },
    h1: {
      uz: "Telegram botga Payme va Click ulash: talablar, narx va jarayon",
      ru: "Подключение Payme и Click к Telegram-боту: требования, цена и процесс",
    },
    description: {
      uz: "Telegram botga Payme yoki Click ulash uchun nima kerak: yuridik shaxs, shartnoma, komissiya va integratsiya. Merchant hali yo'q bo'lsa qanday boshlash mumkin.",
      ru: "Что нужно для подключения Payme или Click к Telegram-боту: юрлицо, договор, комиссия и интеграция. Как начать, если мерчанта пока нет.",
    },
    answer: {
      uz: "Telegram botga Payme yoki Click ulash uchun merchant hisobi kerak: YaTT yoki MChJ, to'lov tizimi bilan shartnoma, hisob raqami va texnik integratsiya. Rasmiylashtirish odatda bir necha kundan bir necha haftagacha vaqt oladi va tushumdan komissiya ushlanadi. Merchant hali yo'q bo'lsa, karta o'tkazmasi va chekni bot orqali tasdiqlash bilan bugunoq boshlash mumkin.",
      ru: "Для подключения Payme или Click к Telegram-боту нужен мерчант-аккаунт: ИП или ООО, договор с платёжной системой, расчётный счёт и техническая интеграция. Оформление обычно занимает от нескольких дней до нескольких недель, и с оборота удерживается комиссия. Если мерчанта пока нет, начать можно уже сегодня — с перевода на карту и подтверждения чека через бота.",
    },
    published: "2026-08-10",
    updated: "2026-08-10",
    category: { uz: "To'lovlar", ru: "Платежи" },
    readTime: { uz: "6 daqiqa", ru: "6 минут" },
    sections: [
      {
        h2: { uz: "Payme va Click botga qanday ulanadi?", ru: "Как Payme и Click подключаются к боту?" },
        html: {
          uz: `<p>Texnik tomondan jarayon uch bosqichdan iborat:</p>
<ol>
<li><strong>Merchant ochish.</strong> To'lov tizimiga ariza berasiz, hujjatlarni topshirasiz va shartnoma imzolaysiz.</li>
<li><strong>Kalitlarni olish.</strong> Merchant tasdiqlangach sizga integratsiya kalitlari (merchant ID va maxfiy kalit) beriladi.</li>
<li><strong>Botga ulash.</strong> Bot to'lov havolasini yaratadi, foydalanuvchi to'laydi, to'lov tizimi botga tasdiq (callback) yuboradi va bot kirish beradi.</li>
</ol>
<p>Ulangandan keyin to'lov <strong>avtomatik</strong> tasdiqlanadi — chekni qo'lda ko'rish kerak bo'lmaydi. Bu katta oqimdagi kanallar uchun asosiy foyda.</p>
<p>Uchinchi qadam — texnik integratsiya — odatda dasturchi ishi. Getolog mijozlari uchun buni jamoamiz bajaradi: merchant hisobingiz tayyor bo'lsa, <a href="https://t.me/getolog_bot" target="_blank" rel="noopener noreferrer">@getolog_bot</a> ga yozing, Payme yoki Click'ni botingizga o'zimiz ulab beramiz.</p>`,
          ru: `<p>С технической стороны процесс состоит из трёх этапов:</p>
<ol>
<li><strong>Открытие мерчанта.</strong> Подаёте заявку в платёжную систему, предоставляете документы и подписываете договор.</li>
<li><strong>Получение ключей.</strong> После одобрения мерчанта вам выдают ключи интеграции (merchant ID и секретный ключ).</li>
<li><strong>Подключение к боту.</strong> Бот создаёт платёжную ссылку, пользователь оплачивает, платёжная система отправляет боту подтверждение (callback), и бот выдаёт доступ.</li>
</ol>
<p>После подключения оплата подтверждается <strong>автоматически</strong> — смотреть чеки вручную не нужно. Это главная выгода для каналов с большим потоком.</p>
<p>Третий шаг — техническая интеграция — обычно работа разработчика. Для клиентов Getolog её выполняет наша команда: если мерчант-аккаунт уже готов, напишите в <a href="https://t.me/getolog_bot" target="_blank" rel="noopener noreferrer">@getolog_bot</a> — мы сами подключим Payme или Click к вашему боту.</p>`,
        },
      },
      {
        h2: { uz: "Talablar: nima kerak bo'ladi?", ru: "Требования: что понадобится?" },
        html: {
          uz: `<p>Merchant ochish uchun odatda quyidagilar so'raladi:</p>
<ul>
<li><strong>Yuridik status</strong> — YaTT yoki MChJ. Jismoniy shaxs sifatida merchant ochib bo'lmaydi.</li>
<li><strong>Bank hisob raqami</strong> — tushum shu yerga tushadi.</li>
<li><strong>Faoliyat turi</strong> — ta'lim xizmatlari yoki raqamli kontent sotuvi hujjatlarda ko'rsatilgan bo'lishi kerak.</li>
<li><strong>Ommaviy oferta</strong> — xizmat shartlari va qaytarish siyosati yozilgan sahifa.</li>
<li><strong>Texnik integratsiya</strong> — callback'larni qabul qiladigan bot yoki server.</li>
</ul>
<p>Aniq ro'yxat va komissiya stavkalari to'lov tizimiga hamda faoliyat turingizga qarab farq qiladi — bularni bevosita Payme yoki Click bilan aniqlashtiring.</p>`,
          ru: `<p>Для открытия мерчанта обычно запрашивают:</p>
<ul>
<li><strong>Юридический статус</strong> — ИП или ООО. Как физическое лицо мерчанта открыть нельзя.</li>
<li><strong>Расчётный счёт в банке</strong> — на него поступает выручка.</li>
<li><strong>Вид деятельности</strong> — образовательные услуги или продажа цифрового контента должны быть отражены в документах.</li>
<li><strong>Публичная оферта</strong> — страница с условиями услуги и политикой возврата.</li>
<li><strong>Техническая интеграция</strong> — бот или сервер, принимающий callback-и.</li>
</ul>
<p>Точный список и ставки комиссии зависят от платёжной системы и вида деятельности — уточняйте их напрямую в Payme или Click.</p>`,
        },
      },
      {
        h2: { uz: "Komissiya, muddat va yashirin xarajatlar", ru: "Комиссия, сроки и скрытые расходы" },
        html: {
          uz: `<p>Merchant qarorini qabul qilishdan oldin uchta narsani hisoblang:</p>
<ul>
<li><strong>Komissiya.</strong> Har bir to'lovdan foiz ushlanadi. 10 mln so'mlik oylik tushumda bu sezilarli summa.</li>
<li><strong>Rasmiylashtirish muddati.</strong> Hujjatlar va tasdiqlash bir necha kundan bir necha haftagacha cho'zilishi mumkin — bu vaqtda kanal sotuvsiz turmasligi kerak.</li>
<li><strong>Buxgalteriya.</strong> Rasmiy tushum soliq va hisobot majburiyatlarini keltiradi.</li>
</ul>
<p>Shu sababli ko'p kanal egalari <strong>bosqichma-bosqich</strong> boradi: avval karta bilan sotuvni yo'lga qo'yadi, daromad barqarorlashgach merchant ochadi.</p>`,
          ru: `<p>Перед решением о мерчанте посчитайте три вещи:</p>
<ul>
<li><strong>Комиссия.</strong> С каждого платежа удерживается процент. При обороте 10 млн сум в месяц это заметная сумма.</li>
<li><strong>Срок оформления.</strong> Документы и одобрение могут занять от нескольких дней до нескольких недель — канал не должен всё это время стоять без продаж.</li>
<li><strong>Бухгалтерия.</strong> Официальная выручка влечёт налоговые и отчётные обязательства.</li>
</ul>
<p>Поэтому многие владельцы каналов идут <strong>поэтапно</strong>: сначала налаживают продажи по карте, а когда доход стабилизируется — открывают мерчанта.</p>`,
        },
      },
      {
        h2: { uz: "Merchant hali yo'q bo'lsa — bugun qanday boshlash mumkin?", ru: "Если мерчанта пока нет — как начать сегодня?" },
        html: {
          uz: `<p>Getolog'da to'lov oqimi merchantsiz ham to'liq ishlaydi:</p>
<ol>
<li>Bot tarifni ko'rsatadi va karta rekvizitini beradi.</li>
<li>Obunachi o'tkazma qilib, chek rasmini yuboradi.</li>
<li>Siz panelda bir tugma bilan tasdiqlaysiz.</li>
<li>Bot bir martalik havolani avtomatik yuboradi va obuna muddatini boshlaydi.</li>
</ol>
<p>Ya'ni yagona qo'lda qoladigan qadam — chekni tasdiqlash. Kirish berish, muddat nazorati, eslatma va <a href="/obuna-tugaganda-kanaldan-chiqarish">avtomatik chiqarish</a> baribir bot tomonidan bajariladi. Keyinchalik merchant ochsangiz, faqat shu bitta qadam avtomatlashadi — qolgan tizim o'zgarmaydi.</p>
<p>To'lov usullarining to'liq taqqoslanishi — <a href="/telegram-kanalga-tolov-qabul-qilish">to'lov qabul qilish sahifasida</a>.</p>`,
          ru: `<p>В Getolog платёжный поток полностью работает и без мерчанта:</p>
<ol>
<li>Бот показывает тариф и выдаёт реквизиты карты.</li>
<li>Подписчик делает перевод и присылает фото чека.</li>
<li>Вы подтверждаете в панели одной кнопкой.</li>
<li>Бот автоматически отправляет одноразовую ссылку и запускает срок подписки.</li>
</ol>
<p>То есть вручную остаётся единственный шаг — подтверждение чека. Выдача доступа, контроль срока, напоминания и <a href="/ru/obuna-tugaganda-kanaldan-chiqarish">автоудаление</a> всё равно выполняются ботом. Если позже вы откроете мерчанта, автоматизируется только этот один шаг — остальная система не изменится.</p>
<p>Полное сравнение способов оплаты — на <a href="/ru/telegram-kanalga-tolov-qabul-qilish">странице о приёме оплаты</a>.</p>`,
        },
      },
      {
        h2: { uz: "Qaysi biri sizga mos?", ru: "Что подходит именно вам?" },
        html: {
          uz: `<table>
<thead><tr><th>Holat</th><th>Tavsiya</th></tr></thead>
<tbody>
<tr><td>Oyiga 50 tagacha to'lov, jismoniy shaxs</td><td>Karta + chek tasdiqlash</td></tr>
<tr><td>Oyiga 50–150 to'lov, YaTT bor</td><td>Karta bilan davom eting, merchantni tayyorlang</td></tr>
<tr><td>Oyiga 150+ to'lov, rasmiy biznes</td><td>Payme / Click merchant</td></tr>
<tr><td>Auditoriya asosan chet elda</td><td>Telegram Stars ni ko'rib chiqing</td></tr>
</tbody>
</table>
<p>Qaysi yo'lni tanlasangiz ham, kanalning asosiy mexanikasi bir xil qoladi: to'lov → tasdiq → bir martalik havola → muddat nazorati. Boshlash uchun <a href="https://t.me/getologbot" target="_blank" rel="noopener noreferrer">@getologbot</a> ga yozing, savol bo'lsa <a href="https://t.me/getolog_bot" target="_blank" rel="noopener noreferrer">@getolog_bot</a> support botiga murojaat qiling.</p>`,
          ru: `<table>
<thead><tr><th>Ситуация</th><th>Рекомендация</th></tr></thead>
<tbody>
<tr><td>До 50 платежей в месяц, физлицо</td><td>Карта + подтверждение чека</td></tr>
<tr><td>50–150 платежей в месяц, есть ИП</td><td>Продолжайте с картой, готовьте мерчанта</td></tr>
<tr><td>150+ платежей в месяц, оформленный бизнес</td><td>Мерчант Payme / Click</td></tr>
<tr><td>Аудитория в основном за рубежом</td><td>Рассмотрите Telegram Stars</td></tr>
</tbody>
</table>
<p>Какой бы путь вы ни выбрали, основная механика канала остаётся той же: оплата → подтверждение → одноразовая ссылка → контроль срока. Чтобы начать, напишите <a href="https://t.me/getologbot" target="_blank" rel="noopener noreferrer">@getologbot</a>; с вопросами — в support-бот <a href="https://t.me/getolog_bot" target="_blank" rel="noopener noreferrer">@getolog_bot</a>.</p>`,
        },
      },
    ],
    faq: [
      {
        q: { uz: "Payme yoki Click ulash uchun yuridik shaxs shartmi?", ru: "Обязательно ли юрлицо для подключения Payme или Click?" },
        a: {
          uz: "Ha, merchant hisobi YaTT yoki MChJ maqomini talab qiladi. Jismoniy shaxs karta o'tkazmasi orqali ishlashi mumkin, lekin merchant ocha olmaydi.",
          ru: "Да, мерчант-аккаунт требует статуса ИП или ООО. Физическое лицо может работать через перевод на карту, но открыть мерчанта не сможет.",
        },
      },
      {
        q: { uz: "Getolog Payme yoki Click'ni ulab beradimi?", ru: "Подключает ли Getolog Payme или Click?" },
        a: {
          uz: "Ha. Merchant hisobingiz tayyor bo'lsa, texnik integratsiyani Getolog jamoasi bajaradi — botingizga Payme yoki Click'ni o'zimiz ulab beramiz. Buning uchun @getolog_bot support botiga yozing.",
          ru: "Да. Если мерчант-аккаунт уже готов, техническую интеграцию выполняет команда Getolog — мы сами подключим Payme или Click к вашему боту. Для этого напишите в support-бот @getolog_bot.",
        },
      },
      {
        q: { uz: "Merchant ochish qancha vaqt oladi?", ru: "Сколько времени занимает открытие мерчанта?" },
        a: {
          uz: "Odatda bir necha kundan bir necha haftagacha — hujjatlarning tayyorligi va faoliyat turiga bog'liq. Shu vaqt ichida karta orqali sotuvni to'xtatmaslik tavsiya qilinadi.",
          ru: "Обычно от нескольких дней до нескольких недель — зависит от готовности документов и вида деятельности. В это время продажи по карте лучше не останавливать.",
        },
      },
      {
        q: { uz: "Komissiya qancha bo'ladi?", ru: "Какой будет комиссия?" },
        a: {
          uz: "Stavka to'lov tizimi va shartnoma shartlariga qarab belgilanadi, shu sababli aniq foizni Payme yoki Click bilan bevosita aniqlashtirish kerak. Karta o'tkazmasida esa komissiya olinmaydi.",
          ru: "Ставка определяется платёжной системой и условиями договора, поэтому точный процент нужно уточнять напрямую в Payme или Click. При переводе на карту комиссия не удерживается.",
        },
      },
      {
        q: { uz: "Merchant ulanganda bot o'zgaradimi?", ru: "Изменится ли бот после подключения мерчанта?" },
        a: {
          uz: "Bot va obunachilar bazasi o'zgarmaydi. Faqat to'lovni tasdiqlash qadami qo'ldan avtomatga o'tadi, qolgan jarayon — havola, muddat, chiqarish — bir xil qoladi.",
          ru: "Бот и база подписчиков не меняются. Автоматизируется только шаг подтверждения оплаты, остальной процесс — ссылка, срок, удаление — остаётся прежним.",
        },
      },
      {
        q: { uz: "Merchantsiz ishlash qonuniymi?", ru: "Законно ли работать без мерчанта?" },
        a: {
          uz: "Karta o'tkazmasi orqali to'lov qabul qilish keng tarqalgan amaliyot, lekin daromad hajmi oshgan sari faoliyatni rasmiylashtirish va soliq masalasini mutaxassis bilan ko'rib chiqish tavsiya etiladi.",
          ru: "Приём оплаты переводом на карту — распространённая практика, но по мере роста дохода стоит обсудить оформление деятельности и налоги со специалистом.",
        },
      },
    ],
    related: ["telegram-kanalga-tolov-qabul-qilish", "telegram-obuna-bot", "getolog-nima"],
    relatedArticles: ["telegram-kanalni-pullik-qilish"],
  },

  /* ─────────────────────────────────────────────────────────────
     5. Obuna tugaganda kanaldan chiqarish
     ───────────────────────────────────────────────────────────── */
  {
    slug: "obuna-tugaganda-kanaldan-chiqarish",
    keyword: { uz: "obuna muddati tugaganda kanaldan chiqarish", ru: "удаление из канала по истечении подписки" },
    title: {
      uz: "Muddati tugagan obunachini Telegram kanaldan avtomatik chiqarish",
      ru: "Автоматическое удаление подписчика с истёкшим сроком из Telegram-канала",
    },
    h1: {
      uz: "Muddati tugagan obunachini Telegram kanaldan avtomatik chiqarish",
      ru: "Автоматическое удаление подписчика с истёкшим сроком из Telegram-канала",
    },
    description: {
      uz: "Obuna muddati tugagan foydalanuvchini Telegram kanaldan avtomatik chiqarish qanday ishlaydi: eslatmalar, chiqarish mexanizmi va qayta kirish jarayoni.",
      ru: "Как работает автоматическое удаление пользователя с истёкшей подпиской из Telegram-канала: напоминания, механизм удаления и повторный вход.",
    },
    answer: {
      uz: "Ha, obuna muddati tugagan foydalanuvchini Telegram kanaldan avtomatik chiqarish mumkin. Bot har bir obunachining tugash sanasini saqlaydi, muddat tugashidan oldin eslatma yuboradi va belgilangan kun kelganda foydalanuvchini kanaldan chiqaradi. Odam qayta to'lov qilsa, bot unga yangi bir martalik havola berib, kanalga qaytaradi.",
      ru: "Да, пользователя с истёкшей подпиской можно удалять из Telegram-канала автоматически. Бот хранит дату окончания каждой подписки, присылает напоминание до её истечения и в назначенный день удаляет пользователя из канала. Если человек оплатит снова, бот выдаст новую одноразовую ссылку и вернёт его в канал.",
    },
    published: "2026-08-10",
    updated: "2026-08-10",
    category: { uz: "Avtomatlashtirish", ru: "Автоматизация" },
    readTime: { uz: "6 daqiqa", ru: "6 минут" },
    sections: [
      {
        h2: { uz: "Muammo: muddati tugaganlar kanalda qolib ketadi", ru: "Проблема: истёкшие подписчики остаются в канале" },
        html: {
          uz: `<p>Pullik kanalning eng sekin sizadigan teshigi — bu <strong>bepul qolib ketgan a'zolar</strong>. Sabab oddiy: kanal egasi 40–50 kishining tugash sanasini yodda tutolmaydi. Natijada:</p>
<ul>
<li>Muddati tugagan odam kontentni bemalol o'qiyverad.</li>
<li>Uni chiqarish "noqulay" bo'lib tuyuladi, chunki vaqt o'tib ketgan.</li>
<li>Boshqa obunachilar buni ko'radi va o'zi ham yangilamay qo'yadi.</li>
</ul>
<p>Hisoblab ko'ring: obuna 100 000 so'm, oyiga 5 ta odam unutilsa — yiliga 6 000 000 so'm yo'qotilgan daromad.</p>`,
          ru: `<p>Самая незаметная дыра платного канала — <strong>участники, оставшиеся бесплатно</strong>. Причина простая: владелец канала не может держать в голове даты окончания у 40–50 человек. В результате:</p>
<ul>
<li>Человек с истёкшим сроком спокойно продолжает читать контент.</li>
<li>Удалять его становится «неудобно», ведь времени прошло много.</li>
<li>Другие подписчики это видят и тоже перестают продлевать.</li>
</ul>
<p>Посчитайте: подписка 100 000 сум, 5 забытых человек в месяц — это 6 000 000 сум упущенного дохода в год.</p>`,
        },
      },
      {
        h2: { uz: "Avtomatik chiqarish qanday ishlaydi?", ru: "Как работает автоматическое удаление?" },
        html: {
          uz: `<p>Getolog'da har bir obunachi uchun tizimda uchta ma'lumot saqlanadi: kim, qaysi tarif va qaysi sanagacha. Shundan keyin jarayon o'zi ketadi:</p>
<ol>
<li><strong>Kunlik tekshiruv.</strong> Tizim har kuni muddati tugayotgan va tugagan obunalarni ko'rib chiqadi.</li>
<li><strong>Ogohlantirish.</strong> Tugashiga bir necha kun qolganda bot foydalanuvchiga eslatma yozadi va yangilash tugmasini beradi.</li>
<li><strong>Chiqarish.</strong> Muddat tugagan kuni bot foydalanuvchini kanaldan chiqaradi.</li>
<li><strong>Qayta kirish yo'li ochiq qoladi.</strong> Odam istagan vaqtda botga qaytib, to'lov qilib, yangi havola olishi mumkin.</li>
</ol>
<p>Muhimi: chiqarish <strong>ban emas</strong> — odam qora ro'yxatga tushmaydi va to'laganidan keyin bemalol qaytadi.</p>`,
          ru: `<p>В Getolog по каждому подписчику в системе хранятся три вещи: кто, какой тариф и до какой даты. Дальше процесс идёт сам:</p>
<ol>
<li><strong>Ежедневная проверка.</strong> Система каждый день просматривает подписки, которые заканчиваются или уже закончились.</li>
<li><strong>Предупреждение.</strong> За несколько дней до окончания бот пишет пользователю напоминание и даёт кнопку продления.</li>
<li><strong>Удаление.</strong> В день окончания срока бот удаляет пользователя из канала.</li>
<li><strong>Путь обратно остаётся открытым.</strong> Человек в любой момент может вернуться в бота, оплатить и получить новую ссылку.</li>
</ol>
<p>Важно: удаление — это <strong>не бан</strong>. Человек не попадает в чёрный список и спокойно возвращается после оплаты.</p>`,
        },
      },
      {
        h2: { uz: "Eslatmalar jadvali", ru: "График напоминаний" },
        html: {
          uz: `<p>Yaxshi ishlaydigan eslatma sxemasi shunday ko'rinadi:</p>
<table>
<thead><tr><th>Qachon</th><th>Xabar mazmuni</th><th>Maqsad</th></tr></thead>
<tbody>
<tr><td>3 kun qolganda</td><td>"Obunangiz 3 kundan keyin tugaydi"</td><td>Odamni ogohlantirish, shoshirmaslik</td></tr>
<tr><td>1 kun qolganda</td><td>"Ertaga kirish yopiladi, yangilaysizmi?"</td><td>Qaror qabul qilishga turtki</td></tr>
<tr><td>Tugagan kuni</td><td>"Obuna tugadi, qaytish uchun shu tugmani bosing"</td><td>Chiqarilgandan keyin qaytarish</td></tr>
</tbody>
</table>
<p>Eslatma matnida <strong>yangilash tugmasi</strong> bo'lishi shart: odam o'ylab o'tirmasdan darhol to'lov qadamiga tushsin. Bu bitta detal yangilanish foizini sezilarli oshiradi.</p>`,
          ru: `<p>Хорошо работающая схема напоминаний выглядит так:</p>
<table>
<thead><tr><th>Когда</th><th>Содержание сообщения</th><th>Цель</th></tr></thead>
<tbody>
<tr><td>За 3 дня</td><td>«Ваша подписка закончится через 3 дня»</td><td>Предупредить, не создавая спешки</td></tr>
<tr><td>За 1 день</td><td>«Завтра доступ закроется, продлеваем?»</td><td>Подтолкнуть к решению</td></tr>
<tr><td>В день окончания</td><td>«Подписка закончилась, нажмите кнопку, чтобы вернуться»</td><td>Вернуть после удаления</td></tr>
</tbody>
</table>
<p>В тексте напоминания обязательно должна быть <strong>кнопка продления</strong>: человек должен сразу попадать на шаг оплаты. Эта одна деталь заметно повышает процент продлений.</p>`,
        },
      },
      {
        h2: { uz: "Qo'lda qilsa qancha vaqt ketadi?", ru: "Сколько времени это займёт вручную?" },
        html: {
          uz: `<p>Bitta obunachini qo'lda boshqarish uchun kerak bo'ladigan ishlar: sanani yozib qo'yish, eslatma yuborish, javobini kutish, to'lovni tekshirish, kanaldan chiqarish. Bu bitta odamga o'rtacha 4–5 daqiqa.</p>
<ul>
<li><strong>50 obunachi:</strong> oyiga ≈ 4 soat faqat muddat boshqaruviga ketadi.</li>
<li><strong>200 obunachi:</strong> oyiga ≈ 15 soat — bu deyarli ikki ish kuni.</li>
</ul>
<p>Va bu ishning eng yomon tomoni — u <strong>uzluksiz</strong>: dam olish kunlari ham kimningdir muddati tugaydi. Avtomatlashtirilganda esa siz faqat chekni tasdiqlaysiz, qolganini tizim bajaradi.</p>`,
          ru: `<p>Что нужно делать вручную по одному подписчику: записать дату, отправить напоминание, дождаться ответа, проверить оплату, удалить из канала. В среднем это 4–5 минут на человека.</p>
<ul>
<li><strong>50 подписчиков:</strong> ≈ 4 часа в месяц только на управление сроками.</li>
<li><strong>200 подписчиков:</strong> ≈ 15 часов в месяц — почти два рабочих дня.</li>
</ul>
<p>И худшее в этой работе то, что она <strong>непрерывная</strong>: сроки заканчиваются и в выходные. При автоматизации вы только подтверждаете чек, остальное делает система.</p>`,
        },
      },
      {
        h2: { uz: "Chiqarilgan odam qaytib kira oladimi?", ru: "Может ли удалённый человек вернуться?" },
        html: {
          uz: `<p>Ha, va aynan shu joyda ko'p pul qaytariladi. Chiqarilgan foydalanuvchi bot bilan aloqada qoladi: u istalgan payt <code>/start</code> bosib, tarif tanlab, qayta to'lov qilishi mumkin. Bot unga <strong>yangi bir martalik havola</strong> beradi — eskisi ishlamaydi.</p>
<p>Eski havolaning ishlamasligi muhim: aks holda bir marta chiqarilgan odam eski linki bilan qaytib kirib olardi. <a href="/blog/invite-link-xavfsizligi">Bir martalik havola</a> shu sababli butun tizimning tayanch nuqtasi hisoblanadi.</p>
<p>Kanalingizni shu tartibda ishlashini xohlasangiz — <a href="https://t.me/getologbot" target="_blank" rel="noopener noreferrer">@getologbot</a> ga <code>/start</code> yuboring, sozlash 2 daqiqa oladi. Yordam kerak bo'lsa <a href="https://t.me/getolog_bot" target="_blank" rel="noopener noreferrer">@getolog_bot</a> support botiga yozing.</p>`,
          ru: `<p>Да, и именно здесь возвращается значительная часть денег. Удалённый пользователь остаётся на связи с ботом: в любой момент он может нажать <code>/start</code>, выбрать тариф и оплатить снова. Бот выдаст ему <strong>новую одноразовую ссылку</strong> — старая уже не работает.</p>
<p>Неработающая старая ссылка принципиальна: иначе однажды удалённый человек просто вернулся бы по прежнему линку. Поэтому <a href="/ru/blog/invite-link-xavfsizligi">одноразовая ссылка</a> — опорная точка всей системы.</p>
<p>Если хотите, чтобы ваш канал работал по такой схеме — отправьте <code>/start</code> боту <a href="https://t.me/getologbot" target="_blank" rel="noopener noreferrer">@getologbot</a>, настройка занимает 2 минуты. Нужна помощь — пишите в support-бот <a href="https://t.me/getolog_bot" target="_blank" rel="noopener noreferrer">@getolog_bot</a>.</p>`,
        },
      },
    ],
    compare: compareCommon,
    faq: [
      {
        q: { uz: "Obuna muddati tugagan foydalanuvchi avtomatik chiqariladimi?", ru: "Удаляется ли пользователь с истёкшей подпиской автоматически?" },
        a: {
          uz: "Ha. Bot har bir obunaning tugash sanasini saqlaydi va muddat tugagan kuni foydalanuvchini kanaldan chiqaradi. Bundan oldin unga eslatma yuboriladi.",
          ru: "Да. Бот хранит дату окончания каждой подписки и в день её истечения удаляет пользователя из канала. Перед этим ему отправляется напоминание.",
        },
      },
      {
        q: { uz: "Chiqarilgan odam qora ro'yxatga tushadimi?", ru: "Попадает ли удалённый человек в чёрный список?" },
        a: {
          uz: "Yo'q. Bu ban emas — foydalanuvchi shunchaki kanaldan chiqariladi va qayta to'lov qilib, yangi havola bilan qaytishi mumkin.",
          ru: "Нет. Это не бан — пользователь просто удаляется из канала и может вернуться, оплатив заново и получив новую ссылку.",
        },
      },
      {
        q: { uz: "Eslatmalar qachon yuboriladi?", ru: "Когда отправляются напоминания?" },
        a: {
          uz: "Odatiy sxema — muddat tugashiga 3 kun va 1 kun qolganda, hamda tugagan kuni. Har bir eslatmada yangilash tugmasi bo'ladi.",
          ru: "Стандартная схема — за 3 дня и за 1 день до окончания, а также в день окончания. В каждом напоминании есть кнопка продления.",
        },
      },
      {
        q: { uz: "Men obunachiga imtiyoz bermoqchi bo'lsam-chi?", ru: "А если я хочу дать подписчику отсрочку?" },
        a: {
          uz: "Muddatni panel orqali qo'lda uzaytirish mumkin — masalan, bir necha kun qo'shib qo'yish. Tizim yangilangan sanaga qarab ishlaydi.",
          ru: "Срок можно продлить вручную через панель — например, добавить несколько дней. Система будет ориентироваться на обновлённую дату.",
        },
      },
      {
        q: { uz: "Bir vaqtning o'zida ko'p odam chiqarilsa kanalga zarar bo'ladimi?", ru: "Не навредит ли каналу удаление многих людей сразу?" },
        a: {
          uz: "Yo'q. Chiqarish jarayoni bosqichma-bosqich amalga oshiriladi va kanalning oddiy ishlashiga ta'sir qilmaydi.",
          ru: "Нет. Удаление выполняется постепенно и не влияет на обычную работу канала.",
        },
      },
      {
        q: { uz: "Guruhda ham shunday ishlaydimi?", ru: "Работает ли это так же в группе?" },
        a: {
          uz: "Ha. Yopiq guruhlarda ham muddat nazorati va avtomatik chiqarish kanaldagi kabi ishlaydi.",
          ru: "Да. В закрытых группах контроль срока и автоудаление работают так же, как в канале.",
        },
      },
    ],
    related: ["telegram-obuna-bot", "getolog-nima", "telegram-kanalga-tolov-qabul-qilish"],
    relatedArticles: ["invite-link-xavfsizligi", "pullik-kanal-uchun-maslahatlar"],
  },
];

export function getLandingPage(slug: string): LandingPage | undefined {
  return landingPages.find((p) => p.slug === slug);
}
