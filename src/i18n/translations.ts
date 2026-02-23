export type Lang = "uz" | "ru";

type T = Record<Lang, string>;

/* ───── Navbar ───── */
export const nav = {
  features: { uz: "Imkoniyatlar", ru: "Возможности" } as T,
  howItWorks: { uz: "Qanday ishlaydi", ru: "Как работает" } as T,
  pricing: { uz: "Tariflar", ru: "Тарифы" } as T,
  faq: { uz: "FAQ", ru: "FAQ" } as T,
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
  phoneBtn1: { uz: "1 oy — 50 000 so'm", ru: "1 месяц — 50 000 сум" } as T,
  phoneBtn2: { uz: "6 oy — 250 000 so'm", ru: "6 месяцев — 250 000 сум" } as T,
  phoneBtn3: { uz: "Doimiy — 500 000 so'm", ru: "Навсегда — 500 000 сум" } as T,
  phoneUserMsg: { uz: "1 oy — 50 000 so'm", ru: "1 месяц — 50 000 сум" } as T,
  phoneCardInfo: {
    uz: "Karta: 8600 **** **** 1234<br/>Summa: 50 000 so'm<br/><br/>To'lovni amalga oshiring va chek rasmini yuboring.",
    ru: "Карта: 8600 **** **** 1234<br/>Сумма: 50 000 сум<br/><br/>Выполните перевод и отправьте фото чека.",
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
        uz: "To'lov tasdiqlangach bot <strong>avtomatik invite link</strong> beradi. Siz faqat tasdiqlaysiz.",
        ru: "После подтверждения оплаты бот <strong>автоматически выдаёт invite-ссылку</strong>. Вы только подтверждаете.",
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
        uz: "Muddat tugashiga <strong>3 va 1 kun</strong> qolganda bot ogohlantiradi. Tugagach — <strong>avtomatik chiqaradi</strong>.",
        ru: "За <strong>3 и 1 день</strong> до окончания бот предупреждает. По истечении — <strong>автоматически удаляет</strong>.",
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
        uz: "Kod yozish shart emas. <strong>Bot tokenini yuboring</strong> — 2 daqiqada tayyor bot olasiz.",
        ru: "Код писать не нужно. <strong>Отправьте токен бота</strong> — и за 2 минуты получите готового бота.",
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
      title: { uz: "Kanal va narxni sozlang", ru: "Настройте канал и цену" } as T,
      text: {
        uz: "Kanal yoki guruhni ulang, obuna narxi va muddatini belgilang, karta raqamingizni kiriting.",
        ru: "Подключите канал или группу, установите цену и срок подписки, введите номер карты.",
      } as T,
    },
    {
      title: { uz: "Bot ishlaydi — siz kuzatasiz", ru: "Бот работает — вы наблюдаете" } as T,
      text: {
        uz: "Obunachilar bot orqali to'lov qiladi, invite link oladi, kanalga kiradi. Hammasi avtomatik.",
        ru: "Подписчики оплачивают через бота, получают invite-ссылку, входят в канал. Всё автоматически.",
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
  standard: { uz: "Standard", ru: "Стандарт" } as T,
  premium: { uz: "Premium", ru: "Премиум" } as T,
  currency: { uz: "so'm", ru: "сум" } as T,
  currencyMonth: { uz: "so'm/oy", ru: "сум/мес" } as T,
  // Features
  feat1bot: { uz: "1 ta bot", ru: "1 бот" } as T,
  feat2bot: { uz: "2 ta bot", ru: "2 бота" } as T,
  feat5bot: { uz: "5 ta bot", ru: "5 ботов" } as T,
  featCard: { uz: "Karta orqali to'lov", ru: "Оплата картой" } as T,
  featStats: { uz: "Statistika", ru: "Статистика" } as T,
  featAuto: { uz: "Avtomatik boshqaruvi", ru: "Автоматическое управление" } as T,
  featNoAd: { uz: "Reklamani o'chirish", ru: "Отключение рекламы" } as T,
  featMultiAdmin: { uz: "Multi-admin", ru: "Мульти-админ" } as T,
  feat2admin: { uz: "2 ta multi-admin", ru: "2 мульти-админа" } as T,
  feat5admin: { uz: "5 ta multi-admin", ru: "5 мульти-админов" } as T,
  featPayme: { uz: "Click / Payme", ru: "Click / Payme" } as T,
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
        uz: "Funksionallik bir xil. Yagona farq — obunachilar botga kirganda Getolog reklamasi ko'rinadi. Pullik tarifda reklama yo'q.",
        ru: "Функционал одинаковый. Единственное отличие — при входе в бот подписчики видят рекламу Getolog. В платном тарифе рекламы нет.",
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
    uz: "Getolog tarif rejalari. Bepul, Standard va Premium tariflarni batafsil taqqoslang.",
    ru: "Тарифные планы Getolog. Подробное сравнение тарифов: Бесплатный, Стандарт и Премиум.",
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
  // Table features
  features: {
    card: {
      name: { uz: "Karta orqali to'lov", ru: "Оплата картой" } as T,
      desc: { uz: "Obunachilar to'g'ridan-to'g'ri karta orqali to'lov qiladi", ru: "Подписчики оплачивают напрямую картой" } as T,
    },
    stats: {
      name: { uz: "Statistika", ru: "Статистика" } as T,
      desc: { uz: "Obunalar, daromad va foydalanuvchilar haqida hisobot", ru: "Отчёт о подписках, доходах и пользователях" } as T,
    },
    auto: {
      name: { uz: "Avtomatik obuna boshqaruvi", ru: "Автоматическое управление подписками" } as T,
      desc: { uz: "Muddat tugashi, eslatma va kanaldan chiqarish avtomatik", ru: "Истечение срока, напоминания и удаление из канала — автоматически" } as T,
    },
    invite: {
      name: { uz: "Bir martalik invite link", ru: "Одноразовая invite-ссылка" } as T,
      desc: { uz: "Har bir to'lov uchun faqat 1 marta ishlaydigan havola", ru: "Ссылка, которая работает только 1 раз для каждой оплаты" } as T,
    },
    welcome: {
      name: { uz: "Custom welcome xabar", ru: "Приветственное сообщение" } as T,
      desc: { uz: "Yangi obunachiga shaxsiy xush kelibsiz xabari", ru: "Персональное приветствие для новых подписчиков" } as T,
    },
    users: {
      name: { uz: "Foydalanuvchilarni boshqarish", ru: "Управление пользователями" } as T,
      desc: { uz: "Obunachilarni ko'rish, boshqarish va blok qilish", ru: "Просмотр, управление и блокировка подписчиков" } as T,
    },
    botLimit: {
      name: { uz: "Bot limiti", ru: "Лимит ботов" } as T,
      desc: { uz: "Bitta akkauntdan nechta bot yaratish mumkinligi", ru: "Сколько ботов можно создать с одного аккаунта" } as T,
    },
    multiAdmin: {
      name: { uz: "Multi-admin", ru: "Мульти-админ" } as T,
      desc: { uz: "Botni boshqa adminlar bilan birgalikda boshqarish", ru: "Совместное управление ботом с другими админами" } as T,
    },
    ads: {
      name: { uz: "Reklama", ru: "Реклама" } as T,
      desc: { uz: "Obunachilar botga kirganda Getolog reklamasi ko'rsatiladi", ru: "Реклама Getolog при входе подписчиков в бот" } as T,
    },
    branding: {
      name: { uz: "Getolog brending", ru: "Брендинг Getolog" } as T,
      desc: {
        uz: '"Ushbu bot @getolog_bot tomonidan ishlab chiqildi" yozuvi ko\'rinadi',
        ru: 'Надпись "Этот бот создан @getolog_bot" отображается в боте',
      } as T,
    },
    receipt: {
      name: { uz: "Chek tasdiqlash usuli", ru: "Способ подтверждения чека" } as T,
      desc: { uz: "To'lov chekini tasdiqlash — qo'lda yoki avtomatik", ru: "Подтверждение чека оплаты — вручную или автоматически" } as T,
    },
    payme: {
      name: { uz: "Click / Payme integratsiya", ru: "Интеграция Click / Payme" } as T,
      desc: { uz: "Click va Payme orqali avtomatik to'lov qabul qilish", ru: "Автоматический приём оплаты через Click и Payme" } as T,
    },
    priority: {
      name: { uz: "Prioritet qo'llab-quvvatlash", ru: "Приоритетная поддержка" } as T,
      desc: { uz: "Tezkor yordam va ustuvor xizmat ko'rsatish", ru: "Быстрая помощь и приоритетное обслуживание" } as T,
    },
  },
  // Mobile card labels
  mBotLimit: { uz: "Bot limiti", ru: "Лимит ботов" } as T,
  mBotLimitDesc: { uz: "Bitta akkauntdan nechta bot", ru: "Сколько ботов с одного аккаунта" } as T,
  mCard: { uz: "Karta orqali to'lov", ru: "Оплата картой" } as T,
  mCardDesc: { uz: "Obunachilar karta orqali to'lov qiladi", ru: "Подписчики оплачивают картой" } as T,
  mStats: { uz: "Statistika", ru: "Статистика" } as T,
  mStatsDesc: { uz: "Obunalar, daromad va foydalanuvchilar hisoboti", ru: "Отчёт о подписках, доходах и пользователях" } as T,
  mAuto: { uz: "Avtomatik obuna boshqaruvi", ru: "Автоматическое управление" } as T,
  mAutoDesc: { uz: "Eslatma va kanaldan chiqarish avtomatik", ru: "Напоминания и удаление из канала — автоматически" } as T,
  mInvite: { uz: "Bir martalik invite link", ru: "Одноразовая invite-ссылка" } as T,
  mInviteDesc: { uz: "Faqat 1 marta ishlaydigan havola", ru: "Ссылка, работающая только 1 раз" } as T,
  mWelcome: { uz: "Custom welcome xabar", ru: "Приветственное сообщение" } as T,
  mWelcomeDesc: { uz: "Shaxsiy xush kelibsiz xabari", ru: "Персональное приветствие" } as T,
  mUsers: { uz: "Foydalanuvchilarni boshqarish", ru: "Управление пользователями" } as T,
  mUsersDesc: { uz: "Ko'rish, boshqarish va blok qilish", ru: "Просмотр, управление и блокировка" } as T,
  mReceipt: { uz: "Chek tasdiqlash", ru: "Подтверждение чека" } as T,
  mReceiptDesc: { uz: "To'lov chekini tasdiqlash usuli", ru: "Способ подтверждения оплаты" } as T,
  mMultiAdmin: { uz: "Multi-admin", ru: "Мульти-админ" } as T,
  mMultiAdminDesc: { uz: "Botni boshqalar bilan boshqarish", ru: "Совместное управление ботом" } as T,
  mPayme: { uz: "Click / Payme", ru: "Click / Payme" } as T,
  mPaymeDesc: { uz: "Avtomatik to'lov qabul qilish", ru: "Автоматический приём оплаты" } as T,
  mAds: { uz: "Reklama", ru: "Реклама" } as T,
  mAdsDesc: { uz: "Botga kirganda Getolog reklamasi", ru: "Реклама Getolog при входе в бот" } as T,
  mBranding: { uz: "Getolog brending", ru: "Брендинг Getolog" } as T,
  mBrandingDesc: {
    uz: '"Ushbu bot @getolog_bot tomonidan ishlab chiqildi" yozuvi',
    ru: 'Надпись "Этот бот создан @getolog_bot"',
  } as T,
  mPriority: { uz: "Prioritet qo'llab-quvvatlash", ru: "Приоритетная поддержка" } as T,
  mPriorityDesc: { uz: "Tezkor yordam va ustuvor xizmat", ru: "Быстрая помощь и приоритет" } as T,
  // Values
  val1: { uz: "1 ta", ru: "1" } as T,
  val2: { uz: "2 ta", ru: "2" } as T,
  val5: { uz: "5 ta", ru: "5" } as T,
  valManual: { uz: "Qo'lda", ru: "Вручную" } as T,
  valAuto: { uz: "Avtomatik", ru: "Автоматически" } as T,
  valYes: { uz: "Bor", ru: "Есть" } as T,
  valNo: { uz: "Yo'q", ru: "Нет" } as T,
};

/* ───── Language helper ───── */
export function langPrefix(lang: Lang): string {
  return lang === "uz" ? "" : "/ru";
}

export function alternateLang(lang: Lang): Lang {
  return lang === "uz" ? "ru" : "uz";
}
