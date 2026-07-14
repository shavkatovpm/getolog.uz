export type Lang = "uz" | "ru";

type T = Record<Lang, string>;

/* ───── Navbar ───── */
export const nav = {
  features: { uz: "Imkoniyatlar", ru: "Возможности" } as T,
  howItWorks: { uz: "Qanday ishlaydi", ru: "Как работает" } as T,
  pricing: { uz: "Tariflar", ru: "Тарифы" } as T,
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
  subtitle: { uz: "Qaysi muammolarni yechamiz?", ru: "Какие проблемы решаем?" } as T,
  solutionTag: { uz: "Yechim", ru: "Решение" } as T,
  cards: [
    {
      pain: {
        uz: "Har bir obunachiga alohida link berish",
        ru: "Отправка отдельной ссылки каждому подписчику",
      } as T,
      desc: {
        uz: "To'lovni tekshirish, link yaratish, kanalga qo'shish — har safar takrorlanadi.",
        ru: "Проверить оплату, создать ссылку, добавить в канал — каждый раз одно и то же.",
      } as T,
      solution: {
        uz: "Payme yoki Click orqali <strong>avtomatik</strong>, xohlasangiz qo'lda chek orqali ham — to'lov tasdiqlangach bot <strong>avtomatik invite link</strong> beradi.",
        ru: "Автоматически через Payme или Click, а при желании — вручную по чеку: после подтверждения оплаты бот <strong>автоматически выдаёт invite-ссылку</strong>.",
      } as T,
    },
    {
      pain: {
        uz: "Obuna muddatini kuzatib bo'lmaydi",
        ru: "Невозможно отследить срок подписки",
      } as T,
      desc: {
        uz: "Kim qachon kirgan, kimniki tugagan — qo'lda nazorat qilish deyarli imkonsiz.",
        ru: "Кто когда вошёл, у кого истёк срок — вручную следить практически невозможно.",
      } as T,
      solution: {
        uz: "Muddat tugashiga <strong>3 va 1 kun</strong> qolganda bot ogohlantiradi. Tugagach — <strong>avtomatik chiqaradi</strong>, so'ng <strong>win-back</strong> xabari bilan qaytishga taklif qiladi.",
        ru: "За <strong>3 и 1 день</strong> до окончания бот предупреждает. По истечении — <strong>автоматически удаляет</strong>, а затем предлагает вернуться через <strong>win-back</strong>.",
      } as T,
    },
    {
      pain: {
        uz: "Link boshqalarga tarqalib ketadi",
        ru: "Ссылка распространяется среди посторонних",
      } as T,
      desc: {
        uz: "Bitta linkni 10 kishi ishlatadi. To'lov qilmaganlar ham kanalingizda o'tiradi.",
        ru: "Одной ссылкой пользуются 10 человек. Те, кто не платил, тоже сидят в вашем канале.",
      } as T,
      solution: {
        uz: "Har bir link <strong>faqat 1 marta</strong> ishlaydi. Obuna bo'ladi, keyin link yaroqsiz holatga keladi.",
        ru: "Каждая ссылка работает <strong>только 1 раз</strong>. Подписчик входит — ссылка становится недействительной.",
      } as T,
    },
    {
      pain: {
        uz: "Bot tayyorlash qimmat va murakkab",
        ru: "Создание бота — дорого и сложно",
      } as T,
      desc: {
        uz: "Dasturchi yollash — o'rtacha 500$. O'zingiz yozish — oylab vaqt oladi.",
        ru: "Нанять разработчика — в среднем 500$. Писать самому — месяцы работы.",
      } as T,
      solution: {
        uz: "Kod yozish shart emas. <strong>Bot tokenini yuboring</strong> — 2 daqiqada tayyor bot olasiz, tariflaringizni (1/3/6/12 oy) o'zingiz sozlaysiz.",
        ru: "Код писать не нужно. <strong>Отправьте токен бота</strong> — за 2 минуты получите готового бота, тарифы (1/3/6/12 мес) настраиваете сами.",
      } as T,
    },
  ],
};

/* ───── How It Works ───── */
export const howItWorks = {
  title: { uz: "3 qadam — bot tayyor", ru: "3 шага — бот готов" } as T,
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
  title: { uz: "Tariflar", ru: "Тарифы" } as T,
  subtitle: { uz: "Kanalingiz hajmiga mos tarifni tanlang", ru: "Выберите тариф, подходящий вашему каналу" } as T,
  badge: { uz: "Tavsiya", ru: "Рекомендуем" } as T,
  startBtn: { uz: "Boshlash", ru: "Начать" } as T,
  compareLink: { uz: "Batafsil taqqoslash →", ru: "Подробное сравнение →" } as T,
  free: { uz: "Bepul", ru: "Бесплатный" } as T,
  start: { uz: "Start", ru: "Старт" } as T,
  pro: { uz: "Pro", ru: "Про" } as T,
  business: { uz: "Biznes", ru: "Бизнес" } as T,
  currency: { uz: "so'm", ru: "сум" } as T,
  currencyMonth: { uz: "so'm/oy", ru: "сум/мес" } as T,
  freeSubs: { uz: "10 obunachigacha (sinov)", ru: "до 10 подписчиков (тест)" } as T,
  startSubs: { uz: "200 obunachigacha", ru: "до 200 подписчиков" } as T,
  proSubs: { uz: "500 obunachigacha", ru: "до 500 подписчиков" } as T,
  businessSubs: { uz: "1000 obunachigacha", ru: "до 1000 подписчиков" } as T,
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
        uz: "Bepul tarifda 10 tagacha obunachi va 1 ta kanal bilan sinab ko'rasiz. Obuna boshqaruvi, muddat nazorati va qo'lda to'lov ishlaydi. Payme/Click avtomatik, referal, win-back va avto-post kabi imkoniyatlar Pro va Biznes tariflarida mavjud.",
        ru: "На бесплатном тарифе — до 10 подписчиков и 1 канал. Управление подписками, контроль срока и оплата вручную работают. Payme/Click автоматически, реферал, win-back и автопостинг доступны на тарифах Pro и Biznes.",
      } as T,
    },
    {
      q: { uz: "Payme yoki Click shart emasmi?", ru: "Обязательно ли подключать Payme или Click?" } as T,
      a: {
        uz: "Yo'q. Qo'lda to'lov (obunachi chek yuboradi, siz bir tugma bilan tasdiqlaysiz) barcha tariflarda ishlaydi. Payme/Click avtomatik integratsiyasi esa Pro va Biznes tariflarida qo'shimcha qulaylik sifatida mavjud.",
        ru: "Нет. Оплата вручную (подписчик отправляет чек, вы подтверждаете одной кнопкой) работает на всех тарифах. Автоматическая интеграция Payme/Click доступна дополнительно на тарифах Pro и Biznes.",
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
  priceTitle: { uz: "Tariflar — Getolog", ru: "Тарифы — Getolog" } as T,
  priceDesc: {
    uz: "Getolog tarif rejalari. Bepul, Start, Pro va Biznes tariflarni batafsil taqqoslang.",
    ru: "Тарифные планы Getolog. Подробное сравнение тарифов: Бесплатный, Старт, Про и Бизнес.",
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
};

/* ───── Price page ───── */
export const pricePage = {
  heroTitle: { uz: "Tariflarni taqqoslang", ru: "Сравните тарифы" } as T,
  heroSubtitle: {
    uz: "Barcha imkoniyatlarni batafsil ko'ring va o'zingizga mos tarifni tanlang",
    ru: "Подробно изучите все возможности и выберите подходящий тариф",
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
  // Values
  valAsosiy: { uz: "Asosiy", ru: "Базовая" } as T,
  valToliq: { uz: "To'liq", ru: "Полная" } as T,
  valToliqExport: { uz: "To'liq + eksport", ru: "Полная + экспорт" } as T,
};

/* ───── Language helper ───── */
export function langPrefix(lang: Lang): string {
  return lang === "uz" ? "" : "/ru";
}

export function alternateLang(lang: Lang): Lang {
  return lang === "uz" ? "ru" : "uz";
}
