export type Lang = "uz" | "ru";

type T = Record<Lang, string>;

/* ───── Navbar ───── */
export const nav = {
  features: { uz: "Imkoniyatlar", ru: "Возможности" } as T,
  howItWorks: { uz: "Qanday ishlaydi", ru: "Как работает" } as T,
  pricing: { uz: "Tarif narxlari", ru: "Тарифы" } as T,
  faq: { uz: "FAQ", ru: "FAQ" } as T,
  blog: { uz: "Maqolalar", ru: "Статьи" } as T,
  start: { uz: "Boshlash", ru: "Начать" } as T,
};

/* ───── Hero ───── */
export const hero = {
  title: {
    uz: 'Yopiq Telegram <span class="hero__br"></span>kanallaringizni <span class="hero__br"></span><span class="highlight">avtomatlashtiring</span>',
    ru: 'Автоматизируйте <span class="hero__br"></span>закрытые Telegram-<span class="hero__br"></span><span class="highlight">каналы</span>',
  } as T,
  subtitle: {
    uz: 'To\'lov qabul qilish, invite link berish, obuna nazorati — <span class="hero__br"></span>barchasini bot bajaradi. Siz faqat kontent joylang.',
    ru: 'Приём оплаты, выдача invite-ссылок, контроль подписки — <span class="hero__br"></span>всё делает бот. Вы только публикуете контент.',
  } as T,
  startBtn: { uz: "Boshlash", ru: "Начать" } as T,
  howBtn: { uz: "Qanday ishlaydi?", ru: "Как работает?" } as T,
  stat1num: { uz: "2 daqiqa", ru: "2 минуты" } as T,
  stat1label: { uz: "sozlash", ru: "настройка" } as T,
  stat2num: { uz: "0 so'm", ru: "0 сум" } as T,
  stat2label: { uz: "boshlash uchun", ru: "чтобы начать" } as T,
  stat3num: { uz: "24/7", ru: "24/7" } as T,
  stat3label: { uz: "bot ishlaydi", ru: "бот работает" } as T,
  // Phone mockup
  phoneName: { uz: "Premium Kanal Bot", ru: "Premium Канал Бот" } as T,
  phoneStatus: { uz: "online", ru: "онлайн" } as T,
  phoneGreeting: {
    uz: 'Assalomu alaykum! "IT Pro Academy" kanaliga kirish uchun to\'lov usulini tanlang:',
    ru: 'Здравствуйте! Для входа в канал "IT Pro Academy" выберите тариф подписки:',
  } as T,
  phoneBtn1: { uz: "1 oy — 100 000 so'm", ru: "1 месяц — 100 000 сум" } as T,
  phoneBtn2: { uz: "3 oy — 270 000 so'm", ru: "3 месяца — 270 000 сум" } as T,
  phoneBtn3: { uz: "12 oy — 960 000 so'm", ru: "12 месяцев — 960 000 сум" } as T,
  phoneUserMsg: { uz: "3 oy — 270 000 so'm", ru: "3 месяца — 270 000 сум" } as T,
  phoneCardInfo: {
    uz: "Karta: 8600 **** **** 1234<br/>Summa: 270 000 so'm<br/><br/>To'lovni amalga oshiring va chek rasmini yuboring.",
    ru: "Карта: 8600 **** **** 1234<br/>Сумма: 270 000 сум<br/><br/>Выполните перевод и отправьте фото чека.",
  } as T,
  phoneSuccess: {
    uz: 'To\'lov tasdiqlandi! Mana sizning linkingiz:<br/><br/><span class="invite-link">t.me/+aBcDeFgHiJk</span><br/><br/>Bu link faqat 1 marta ishlaydi.',
    ru: 'Оплата подтверждена! Вот ваша ссылка:<br/><br/><span class="invite-link">t.me/+aBcDeFgHiJk</span><br/><br/>Эта ссылка работает только 1 раз.',
  } as T,
};

/* ───── Problems / Features ───── */
export const problems = {
  title: { uz: "Getolog imkoniyatlari", ru: "Возможности Getolog" } as T,
  subtitle: {
    uz: "Kanalingiz uchun kerak bo'lgan hamma narsa — bitta botda",
    ru: "Всё, что нужно для вашего канала — в одном боте",
  } as T,
  groups: [
    {
      name: { uz: "To'lov", ru: "Оплата" } as T,
      items: [
        {
          icon: "card",
          title: { uz: "Avtomatik to'lov", ru: "Автоматическая оплата" } as T,
          text: {
            uz: "Payme yoki Click orqali to'lov qilinishi bilan obunachi kanalga darhol qo'shiladi",
            ru: "После оплаты через Payme или Click подписчик сразу добавляется в канал",
          } as T,
        },
        {
          icon: "receipt",
          title: { uz: "Qo'lda to'lov", ru: "Оплата вручную" } as T,
          text: {
            uz: "Integratsiyasiz ham ishlaydi — chek yuboriladi, bir tugma bilan tasdiqlaysiz",
            ru: "Работает и без интеграции — чек отправляется, вы подтверждаете одной кнопкой",
          } as T,
        },
        {
          icon: "link",
          title: { uz: "Bir martalik havola", ru: "Одноразовая ссылка" } as T,
          text: {
            uz: "Har bir to'lov uchun alohida link — begonalar kira olmaydi",
            ru: "Отдельная ссылка для каждой оплаты — посторонние не смогут войти",
          } as T,
        },
      ],
    },
    {
      name: { uz: "Nazorat", ru: "Контроль" } as T,
      items: [
        {
          icon: "clock",
          title: { uz: "Muddat nazorati", ru: "Контроль срока" } as T,
          text: {
            uz: "Obuna tugaganda kanaldan avtomatik chiqariladi, siz kuzatib turmaysiz",
            ru: "По истечении подписки бот автоматически удаляет из канала — следить вручную не нужно",
          } as T,
        },
        {
          icon: "bell",
          title: { uz: "Eslatma tizimi", ru: "Напоминания" } as T,
          text: {
            uz: "Muddat tugashiga 3 va 1 kun qolganda obunachiga avtomatik xabar boradi",
            ru: "За 3 и 1 день до окончания подписчику приходит автоматическое напоминание",
          } as T,
        },
        {
          icon: "sliders",
          title: { uz: "Moslashuvchan tariflar", ru: "Гибкие тарифы" } as T,
          text: {
            uz: "1, 3, 6 yoki 12 oylik rejalar — narxni o'zingiz belgilaysiz",
            ru: "Планы на 1, 3, 6 или 12 месяцев — цену устанавливаете сами",
          } as T,
        },
      ],
    },
    {
      name: { uz: "O'sish", ru: "Рост" } as T,
      items: [
        {
          icon: "users",
          title: { uz: "Referal tizimi", ru: "Реферальная система" } as T,
          text: {
            uz: "Obunachi yangi a'zo taklif qilsa, bonus oladi — kanal o'z-o'zidan o'sadi",
            ru: "Подписчик получает бонус за приглашённого друга — канал растёт сам",
          } as T,
        },
        {
          icon: "refresh",
          title: { uz: "Win-back", ru: "Win-back" } as T,
          text: {
            uz: "Ketgan obunachiga avtomatik qaytish taklifi — yo'qolgan daromadni qaytaring",
            ru: "Автоматическое предложение вернуться ушедшему подписчику — верните упущенный доход",
          } as T,
        },
        {
          icon: "calendar",
          title: { uz: "Avto-post", ru: "Автопостинг" } as T,
          text: {
            uz: "Postlarni belgilangan vaqtda joylang va avtomatik o'chiring",
            ru: "Публикуйте посты по расписанию и удаляйте автоматически",
          } as T,
        },
      ],
    },
    {
      name: { uz: "Boshqaruv", ru: "Управление" } as T,
      items: [
        {
          icon: "layers",
          title: { uz: "Ko'p kanal", ru: "Несколько каналов" } as T,
          text: {
            uz: "Bitta bot orqali bir nechta kanalni boshqaring",
            ru: "Управляйте несколькими каналами через одного бота",
          } as T,
        },
        {
          icon: "chart",
          title: { uz: "Analitika", ru: "Аналитика" } as T,
          text: {
            uz: "Daromad, obunachilar va chiqib ketganlar — bir joyda, real vaqtda",
            ru: "Доход, подписчики и отток — всё в одном месте, в реальном времени",
          } as T,
        },
        {
          icon: "id",
          title: { uz: "Mini-CRM", ru: "Мини-CRM" } as T,
          text: {
            uz: "Har bir obunachi bo'yicha to'liq tarix va karta",
            ru: "Полная карточка и история по каждому подписчику",
          } as T,
        },
      ],
    },
  ],
};

/* ───── How It Works ───── */
export const howItWorks = {
  title: { uz: "3 qadamda tayyor", ru: "3 шага — бот готов" } as T,
  subtitle: { uz: "Texnik bilim talab qilinmaydi", ru: "Технические знания не требуются" } as T,
  steps: [
    {
      title: { uz: "Bot yarating va tokenni yuboring", ru: "Создайте бота и отправьте токен" } as T,
      text: {
        uz: "@BotFather orqali bot yarating. Tokenni Getolog botiga yuboring.",
        ru: "Создайте бота через @BotFather. Отправьте токен боту Getolog.",
      } as T,
    },
    {
      title: { uz: "Kanal va tariflarni sozlang", ru: "Настройте канал и тарифы" } as T,
      text: {
        uz: "Kanal yoki guruhni ulang, 1/3/6/12 oylik tariflarni belgilang, Payme/Click yoki karta raqamingizni kiriting.",
        ru: "Подключите канал или группу, задайте тарифы на 1/3/6/12 месяцев, укажите Payme/Click или номер карты.",
      } as T,
    },
    {
      title: { uz: "Bot ishlaydi — siz kuzatasiz", ru: "Бот работает — вы наблюдаете" } as T,
      text: {
        uz: "Obunachilar bot orqali to'lov qiladi, invite link oladi, kanalga kiradi. Muddat tugasa — avtomatik chiqadi, ketganlarga win-back taklifi boradi. Hammasi avtomatik.",
        ru: "Подписчики оплачивают через бота, получают invite-ссылку, входят в канал. Истёк срок — автоматически удаляются, ушедшим приходит win-back. Всё автоматически.",
      } as T,
    },
  ],
};

/* ───── Pricing ───── */
export const pricing = {
  title: { uz: "Tarif narxlari", ru: "Тарифы" } as T,
  subtitle: { uz: "Mos tarifni tanlang", ru: "Выберите тариф, подходящий вашему каналу" } as T,
  badge: { uz: "Tavsiya", ru: "Рекомендуем" } as T,
  startBtn: { uz: "Boshlash", ru: "Начать" } as T,
  compareLink: { uz: "Batafsil taqqoslash →", ru: "Подробное сравнение →" } as T,
  free: { uz: "Bepul", ru: "Бесплатный" } as T,
  minimal: { uz: "Minimal", ru: "Минимал" } as T,
  start: { uz: "Standart", ru: "Стандарт" } as T,
  pro: { uz: "Pro", ru: "Про" } as T,
  business: { uz: "Biznes", ru: "Бизнес" } as T,
  currency: { uz: "so'm", ru: "сум" } as T,
  currencyMonth: { uz: "so'm/oy", ru: "сум/мес" } as T,
  freeSubs: { uz: "20 faol obunachi", ru: "до 20 подписчиков" } as T,
  minimalSubs: { uz: "100 faol obunachi", ru: "до 100 подписчиков" } as T,
  startSubs: { uz: "200 faol obunachi", ru: "до 200 подписчиков" } as T,
  proSubs: { uz: "500 faol obunachi", ru: "до 500 подписчиков" } as T,
  businessSubs: { uz: "1000 faol obunachi", ru: "до 1000 подписчиков" } as T,
  // Features (teaser card lines)
  featSubs: { uz: "Faol obunachi", ru: "Активные подписчики" } as T,
  featChannels: { uz: "Kanal soni", ru: "Количество каналов" } as T,
  featManualPay: { uz: "Qo'lda to'lov tasdiqlash", ru: "Подтверждение оплаты вручную" } as T,
  featExpiry: { uz: "Muddat nazorati + eslatma", ru: "Контроль срока + напоминания" } as T,
  featPlans: { uz: "Tarif rejalari (1/3/6/12 oy)", ru: "Тарифные планы (1/3/6/12 мес)" } as T,
  featPayme: { uz: "Payme / Click avtomatik", ru: "Payme / Click автоматически" } as T,
  featReferral: { uz: "Referal + Win-back", ru: "Реферал + Win-back" } as T,
  featAutopost: { uz: "Avto-post", ru: "Автопостинг" } as T,
  featCRM: { uz: "Mini-CRM", ru: "Мини-CRM" } as T,
  featBranding: { uz: "Getolog brendi ko'rsatiladi", ru: "Отображается брендинг Getolog" } as T,
};

/* ───── FAQ ───── */
export const faq = {
  title: { uz: "Ko'p so'raladigan savollar", ru: "Часто задаваемые вопросы" } as T,
  items: [
    {
      q: { uz: "Getolog qanday ishlaydi?", ru: "Как работает Getolog?" } as T,
      a: {
        uz: "Bot tokeningizni yuborasiz — Getolog undan sotuvchi bot yasaydi. Obunachilar shu bot orqali to'lov qiladi va bir martalik invite link oladi.",
        ru: "Вы отправляете токен бота — Getolog создаёт из него бота-продавца. Подписчики оплачивают через этого бота и получают одноразовую invite-ссылку.",
      } as T,
    },
    {
      q: { uz: "To'lov qayerga tushadi?", ru: "Куда поступает оплата?" } as T,
      a: {
        uz: "To'g'ridan-to'g'ri sizning kartangizga. Getolog to'lovga tegmaydi — faqat bot va obuna boshqaruvini ta'minlaydi.",
        ru: "Напрямую на вашу карту. Getolog не касается оплаты — обеспечивает только управление ботом и подписками.",
      } as T,
    },
    {
      q: { uz: "Link ulashib yuborishsa nima bo'ladi?", ru: "Что будет, если ссылку передадут другим?" } as T,
      a: {
        uz: "Har bir link faqat 1 marta ishlaydi. Birinchi kirgan oladi — qolganlar uchun link yaroqsiz bo'ladi.",
        ru: "Каждая ссылка работает только 1 раз. Первый вошедший получает доступ — для остальных ссылка становится недействительной.",
      } as T,
    },
    {
      q: { uz: "Obuna muddati tugasa?", ru: "Что происходит, когда подписка истекает?" } as T,
      a: {
        uz: "3 kun va 1 kun qolganda ogohlantirish yuboriladi. Muddat tugagach — avtomatik kanaldan chiqariladi.",
        ru: "За 3 дня и за 1 день отправляется предупреждение. По истечении срока — автоматическое удаление из канала.",
      } as T,
    },
    {
      q: { uz: "Bepul tarifda cheklovi bormi?", ru: "Есть ли ограничения в бесплатном тарифе?" } as T,
      a: {
        uz: "Bepul tarifda 20 tagacha obunachi va 1 ta kanal bilan sinab ko'rasiz. Obuna boshqaruvi, muddat nazorati va qo'lda to'lov ishlaydi, bot ichida Getolog brendi ko'rsatiladi. Payme/Click avtomatik to'lov Standart tarifidan boshlab, referal, win-back va avto-post esa Pro va Biznes tariflarida mavjud.",
        ru: "На бесплатном тарифе — до 20 подписчиков и 1 канал. Управление подписками, контроль срока и оплата вручную работают, в боте отображается брендинг Getolog. Payme/Click автоматически — начиная с тарифа Standart, а реферал, win-back и автопостинг — на тарифах Pro и Biznes.",
      } as T,
    },
    {
      q: { uz: "Payme yoki Click shart emasmi?", ru: "Обязательно ли подключать Payme или Click?" } as T,
      a: {
        uz: "Yo'q. Qo'lda to'lov (obunachi chek yuboradi, siz bir tugma bilan tasdiqlaysiz) barcha tariflarda ishlaydi. Payme/Click avtomatik integratsiyasi esa Standart, Pro va Biznes tariflarida qo'shimcha qulaylik sifatida mavjud.",
        ru: "Нет. Оплата вручную (подписчик отправляет чек, вы подтверждаете одной кнопкой) работает на всех тарифах. Автоматическая интеграция Payme/Click доступна дополнительно на тарифах Standart, Pro и Biznes.",
      } as T,
    },
    {
      q: { uz: "Referal va win-back nima?", ru: "Что такое реферал и win-back?" } as T,
      a: {
        uz: "Referal — obunachingiz yangi a'zo taklif qilsa, unga bonus beriladi. Win-back — muddati tugab ketgan obunachiga avtomatik qaytish taklifi yuboriladi. Ikkalasi ham Pro va Biznes tariflarida mavjud.",
        ru: "Реферал — бонус подписчику, приведшему нового участника. Win-back — автоматическое предложение вернуться тем, у кого истёк срок. Оба доступны на тарифах Pro и Biznes.",
      } as T,
    },
    {
      q: { uz: "Bot tokenimni berib xavfsizmi?", ru: "Безопасно ли передавать токен бота?" } as T,
      a: {
        uz: "Ha. Token shifrlangan holda saqlanadi. Xohlagan vaqtda tokenni o'zgartirishingiz mumkin.",
        ru: "Да. Токен хранится в зашифрованном виде. Вы можете сменить токен в любое время.",
      } as T,
    },
  ],
};

/* ───── CTA ───── */
export const cta = {
  title: { uz: "Kanalingizni avtomatlashtirishga tayyormisiz?", ru: "Готовы автоматизировать свой канал?" } as T,
  subtitle: { uz: "2 daqiqada sozlang. Bepul boshlang.", ru: "Настройте за 2 минуты. Начните бесплатно." } as T,
  btn: { uz: "Telegram'da boshlash", ru: "Начать в Telegram" } as T,
};

/* ───── Footer ───── */
export const footer = {
  tagline: { uz: "Yopiq kanallar uchun avtomatlashtirish", ru: "Автоматизация закрытых каналов" } as T,
  bot: { uz: "Bot", ru: "Бот" } as T,
  help: { uz: "Yordam", ru: "Помощь" } as T,
  blog: { uz: "Maqolalar", ru: "Статьи" } as T,
  info: { uz: "Ma'lumot", ru: "Информация" } as T,
  offerta: { uz: "Offerta", ru: "Оферта" } as T,
  copyright: { uz: "© 2026 Getolog. Barcha huquqlar himoyalangan.", ru: "© 2026 Getolog. Все права защищены." } as T,
};

/* ───── 404 ───── */
export const notFound = {
  title: { uz: "404 — Sahifa topilmadi | Getolog", ru: "404 — Страница не найдена | Getolog" } as T,
  desc: { uz: "Kechirasiz, siz qidirayotgan sahifa topilmadi.", ru: "К сожалению, запрашиваемая страница не найдена." } as T,
  heading: { uz: "Sahifa topilmadi", ru: "Страница не найдена" } as T,
  text: {
    uz: "Kechirasiz, siz qidirayotgan sahifa mavjud emas yoki ko'chirilgan.",
    ru: "К сожалению, запрашиваемая страница не существует или была перемещена.",
  } as T,
  btn: { uz: "Bosh sahifaga qaytish", ru: "Вернуться на главную" } as T,
};

/* ───── Layout / Meta ───── */
export const meta = {
  defaultDesc: {
    uz: "Getolog — Telegram kanalingizni pullik qiling. Bot tokeningizni yuboring, biz avtomatlashtirilgan sotuvchi bot yaratamiz.",
    ru: "Getolog — монетизируйте свой Telegram-канал. Отправьте токен бота, и мы создадим автоматизированного бота-продавца.",
  } as T,
  homeTitle: {
    uz: "Getolog — Telegram kanal/guruhni monetizatsiya qiling",
    ru: "Getolog — монетизация Telegram-каналов и групп",
  } as T,
  priceTitle: { uz: "Telegram obuna bot narxi — Getolog tariflari", ru: "Цена бота подписки Telegram — тарифы Getolog" } as T,
  priceDesc: {
    uz: "Telegram obuna bot narxi qancha? Bepul, Minimal, Standart, Pro va Biznes tariflarni to'liq taqqoslang — 20 tadan 1000 tagacha obunachi uchun mos variantni tanlang.",
    ru: "Сколько стоит бот подписки Telegram? Сравните тарифы Bepul, Minimal, Standart, Pro и Biznes — от 20 до 1000 подписчиков.",
  } as T,
  skipLink: { uz: "Asosiy kontentga o'tish", ru: "Перейти к основному контенту" } as T,
  infoTitle: { uz: "Getolog haqida — Ma'lumot", ru: "О сервисе Getolog — Информация" } as T,
  infoDesc: {
    uz: "Getolog nima, qanday ishlaydi, kimga mo'ljallangan — batafsil ma'lumot.",
    ru: "Что такое Getolog, как работает, для кого предназначен — подробная информация.",
  } as T,
  offertaTitle: { uz: "Ommaviy oferta — Getolog", ru: "Публичная оферта — Getolog" } as T,
  offertaDesc: {
    uz: "Getolog xizmati ommaviy oferta shartnomasi. Xizmat ko'rsatish shartlari.",
    ru: "Публичная оферта сервиса Getolog. Условия оказания услуг.",
  } as T,
  blogTitle: { uz: "Maqolalar — Getolog", ru: "Статьи — Getolog" } as T,
  blogDesc: {
    uz: "Telegram kanalni monetizatsiya qilish, obuna boshqaruvi va bot sozlash haqida foydali maqolalar.",
    ru: "Полезные статьи о монетизации Telegram-каналов, управлении подписками и настройке ботов.",
  } as T,
  arizaTitle: { uz: "Ariza qoldiring — Getolog", ru: "Оставьте заявку — Getolog" } as T,
  arizaDesc: {
    uz: "Kanalingizni Getolog bilan avtomatlashtirish uchun ariza qoldiring — jamoamiz siz bilan bog'lanadi.",
    ru: "Оставьте заявку, чтобы автоматизировать свой канал с Getolog — наша команда свяжется с вами.",
  } as T,
};

/* ───── Price page ───── */
export const pricePage = {
  heroTitle: { uz: 'Telegram obuna bot narxi<br/><span class="price-hero__hand">barcha tariflarni solishtiring</span>', ru: 'Цена бота подписки Telegram<br/><span class="price-hero__hand">сравните все тарифы</span>' } as T,
  heroSubtitle: {
    uz: "Har oylik narx, obunachi chegarasi va imkoniyatlarni bir joyda ko'ring va o'zingizga mos tarifni tanlang",
    ru: "Ежемесячная цена, лимит подписчиков и возможности — всё в одном месте",
  } as T,
  priceIntro: {
    uz: "Telegram obuna bot narxi kanalingiz hajmiga — faol obunachilar soniga va kerakli imkoniyatlarga (Payme/Click avtomatik to'lov, referal, avto-post) bog'liq. Bepul tarifda 20 tagacha obunachi bilan sinab ko'rasiz, kanal o'sgani sayin yuqoriroq tarifga o'tasiz.",
    ru: "Цена бота подписки Telegram зависит от размера канала — числа активных подписчиков и нужных функций (автооплата Payme/Click, реферал, автопостинг). На бесплатном тарифе можно протестировать с 20 подписчиками, а по мере роста канала — перейти на более высокий тариф.",
  } as T,
  featureCol: { uz: "Imkoniyat", ru: "Возможность" } as T,
  ctaTitle: { uz: "Boshlashga tayyormisiz?", ru: "Готовы начать?" } as T,
  ctaSubtitle: { uz: "2 daqiqada sozlang. Bepul boshlang.", ru: "Настройте за 2 минуты. Начните бесплатно." } as T,
  scaleNote: {
    uz: "1000 dan ortiq obunachi? Scale rejasi: $150 dan boshlab, har qo'shimcha 100 obunachi uchun +$10, har qo'shimcha kanal uchun +$15.",
    ru: "Более 1000 подписчиков? План Scale: от $150, +$10 за каждые дополнительные 100 подписчиков, +$15 за каждый доп. канал.",
  } as T,
  // Table features
  features: {
    subs: {
      name: { uz: "Faol obunachi", ru: "Активные подписчики" } as T,
      desc: { uz: "Bir vaqtda boshqarilishi mumkin bo'lgan obunachilar soni", ru: "Сколько подписчиков можно вести одновременно" } as T,
    },
    channels: {
      name: { uz: "Kanal soni", ru: "Количество каналов" } as T,
      desc: { uz: "Bitta hisobda ulash mumkin bo'lgan kanal/guruh soni", ru: "Сколько каналов/групп можно подключить на аккаунт" } as T,
    },
    manage: {
      name: { uz: "Obunachi boshqaruvi", ru: "Управление подписчиками" } as T,
      desc: { uz: "To'lov evaziga qo'shish, chiqarish, qayta kirish imkoni", ru: "Добавление по оплате, удаление, повторный вход" } as T,
    },
    expiry: {
      name: { uz: "Muddat nazorati + eslatma", ru: "Контроль срока + напоминания" } as T,
      desc: { uz: "Muddat tugashiga 3 va 1 kun qolganda ogohlantirish, so'ng avtomatik chiqarish", ru: "Уведомление за 3 и 1 день до истечения, затем автоудаление" } as T,
    },
    manualPay: {
      name: { uz: "Qo'lda to'lov", ru: "Оплата вручную" } as T,
      desc: { uz: "Integratsiyasiz ham ishlaydi — chek yuboriladi, bir tugma bilan tasdiqlanadi", ru: "Работает и без интеграции — чек отправляется, подтверждается одной кнопкой" } as T,
    },
    plans: {
      name: { uz: "Tarif rejalari (1/3/6/12 oy)", ru: "Тарифные планы (1/3/6/12 мес)" } as T,
      desc: { uz: "Obunachilar uchun moslashuvchan muddatlar, uzoq muddatga chegirma", ru: "Гибкие сроки для подписчиков, скидка за долгий срок" } as T,
    },
    payme: {
      name: { uz: "Payme / Click avtomatik", ru: "Payme / Click автоматически" } as T,
      desc: { uz: "Obunachi to'laydi, bot o'zi kanalga qo'shadi", ru: "Подписчик платит — бот сам добавляет в канал" } as T,
    },
    analytics: {
      name: { uz: "Analitika", ru: "Аналитика" } as T,
      desc: { uz: "Obunachilar, daromad va chiqib ketganlar statistikasi", ru: "Статистика подписчиков, дохода и оттока" } as T,
    },
    referral: {
      name: { uz: "Referal + Win-back", ru: "Реферал + Win-back" } as T,
      desc: { uz: "Yangi a'zo olib kelganga bonus, ketganlarga avtomatik qaytish taklifi", ru: "Бонус за приглашённых, автопредложение вернуться ушедшим" } as T,
    },
    autopost: {
      name: { uz: "Avto-post", ru: "Автопостинг" } as T,
      desc: { uz: "Postlarni belgilangan vaqtda joylash va avtomatik o'chirish", ru: "Публикация постов по расписанию и автоудаление" } as T,
    },
    cleanup: {
      name: { uz: "Deleted-akkaunt tozalash", ru: "Очистка удалённых аккаунтов" } as T,
      desc: { uz: "O'chirilgan Telegram akkauntlarni ro'yxatdan avtomatik tozalaydi", ru: "Автоматически удаляет из списка удалённые Telegram-аккаунты" } as T,
    },
    crm: {
      name: { uz: "Mini-CRM", ru: "Мини-CRM" } as T,
      desc: { uz: "Har bir obunachi bo'yicha batafsil karta va tarix", ru: "Подробная карточка и история по каждому подписчику" } as T,
    },
    branding: {
      name: { uz: "Getolog brendi ko'rsatiladi", ru: "Отображается брендинг Getolog" } as T,
      desc: { uz: "Obunachi botga kirganda Getolog logotipi/nomi ko'rinadi", ru: "При входе подписчика в бот виден логотип/название Getolog" } as T,
    },
  },
  // Mobile card labels (mirror of features, shorter)
  mSubs: { uz: "Faol obunachi", ru: "Активные подписчики" } as T,
  mChannels: { uz: "Kanal soni", ru: "Количество каналов" } as T,
  mManage: { uz: "Obunachi boshqaruvi", ru: "Управление подписчиками" } as T,
  mExpiry: { uz: "Muddat nazorati + eslatma", ru: "Контроль срока + напоминания" } as T,
  mManualPay: { uz: "Qo'lda to'lov", ru: "Оплата вручную" } as T,
  mPlans: { uz: "Tarif rejalari (1/3/6/12 oy)", ru: "Тарифные планы (1/3/6/12 мес)" } as T,
  mPayme: { uz: "Payme / Click avtomatik", ru: "Payme / Click автоматически" } as T,
  mAnalytics: { uz: "Analitika", ru: "Аналитика" } as T,
  mReferral: { uz: "Referal + Win-back", ru: "Реферал + Win-back" } as T,
  mAutopost: { uz: "Avto-post", ru: "Автопостинг" } as T,
  mCleanup: { uz: "Deleted-akkaunt tozalash", ru: "Очистка удалённых аккаунтов" } as T,
  mCRM: { uz: "Mini-CRM", ru: "Мини-CRM" } as T,
  mBranding: { uz: "Getolog brendi ko'rsatiladi", ru: "Отображается брендинг Getolog" } as T,
  // Values
  valAsosiy: { uz: "Asosiy", ru: "Базовая" } as T,
  valToliq: { uz: "To'liq", ru: "Полная" } as T,
  valToliqExport: { uz: "To'liq + eksport", ru: "Полная + экспорт" } as T,
};

/* ───── Ariza forma ───── */
export const ariza = {
  title: { uz: "Ariza qoldiring", ru: "Оставьте заявку" } as T,
  subtitle: {
    uz: "Kanalingiz haqida qisqacha ma'lumot bering — bizning jamoa siz bilan tez orada bog'lanadi.",
    ru: "Расскажите коротко о своём канале — наша команда свяжется с вами в ближайшее время.",
  } as T,
  fullName: { uz: "To'liq ismingiz", ru: "Ваше полное имя" } as T,
  fullNamePlaceholder: { uz: "Vali Aliyev", ru: "Иван Иванов" } as T,
  phoneNumber: { uz: "Telefon raqamingiz", ru: "Ваш номер телефона" } as T,
  phoneNumberPlaceholder: { uz: "+998 90 123 45 67", ru: "+998 90 123 45 67" } as T,
  telegramUsername: { uz: "Telegram username", ru: "Telegram username" } as T,
  telegramPlaceholder: { uz: "@username", ru: "@username" } as T,
  channelTopic: { uz: "Kanal mavzusi", ru: "Тема канала" } as T,
  channelTopicPlaceholder: {
    uz: "Masalan: onlayn ingliz tili kursi",
    ru: "Например: онлайн-курс английского языка",
  } as T,
  subscriberCount: { uz: "Obunachilar soni (taxminan)", ru: "Количество подписчиков (примерно)" } as T,
  subscriberPlaceholder: { uz: "masalan, 500", ru: "например, 500" } as T,
  message: { uz: "Xabaringiz", ru: "Ваше сообщение" } as T,
  messagePlaceholder: {
    uz: "Nima haqida bog'lanmoqchisiz?",
    ru: "О чём хотите рассказать?",
  } as T,
  submitBtn: { uz: "Ariza yuborish", ru: "Отправить заявку" } as T,
  submittingBtn: { uz: "Yuborilmoqda...", ru: "Отправка..." } as T,
  successMsg: {
    uz: "Arizangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.",
    ru: "Ваша заявка принята! Мы свяжемся с вами в ближайшее время.",
  } as T,
  errorMsg: {
    uz: "Xatolik yuz berdi. Birozdan keyin qayta urinib ko'ring.",
    ru: "Произошла ошибка. Попробуйте ещё раз чуть позже.",
  } as T,
  rateLimitMsg: {
    uz: "Bir daqiqada faqat 1 marta yuborish mumkin. Biroz kuting.",
    ru: "Отправка возможна раз в минуту. Немного подождите.",
  } as T,
};

/* ───── Language helper ───── */
export function langPrefix(lang: Lang): string {
  return lang === "uz" ? "" : "/ru";
}

export function alternateLang(lang: Lang): Lang {
  return lang === "uz" ? "ru" : "uz";
}
