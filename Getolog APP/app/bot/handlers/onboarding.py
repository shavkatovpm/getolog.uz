"""Bosh bot oqimi: /start -> ism -> bot tokeni -> webhook -> kanalga ulash + huquq tekshirish.

Bu faylda ikkita alohida router bor, chunki ikki xil bot ularni ishlatadi:
- `main_router` — GETOLOG bosh boti bilan suhbatda (admin ro'yxatdan o'tadi).
- `child_router` — adminning shaxsiy boti bilan bog'liq (kanalga admin qilib
  qo'shilganini bazada jimgina qayd etish uchun `my_chat_member` hodisasini
  tinglaydi — adminga xabar shu yerdan YUBORILMAYDI, faqat holat saqlanadi).

Kanalga admin qilib qo'shilganini bilish faqat bitta yo'l bilan bo'ladi: admin
"✅ Admin qildim" tugmasini bosganda, bazada (`my_chat_member` orqali) allaqachon
qayd etilgan eng so'nggi holat o'qib ko'rsatiladi. Bitta bot bir nechta kanalga
admin qilib qo'shilishi mumkin — shuning uchun holat har doim RO'YXAT sifatida
ko'rsatiladi, bitta emas.
"""

import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ChatMemberAdministrator, ChatMemberUpdated, Message
from aiogram.utils.token import TokenValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot import keyboards, registry
from app.bot.keyboards import TARIFF_LABELS
from app.bot.states import OnboardingStates
from app.config import settings
from app.db.models import Admin, Bot as BotModel, Channel, ChatType
from app.services import channel_service
from app.services.encryption import encrypt_token
from app.services.login_codes import generate_login_code
from app.services.subscription_service import can_add_channel

logger = logging.getLogger(__name__)

main_router = Router(name="onboarding_main")
child_router = Router(name="onboarding_child")


async def _get_admin(session: AsyncSession, telegram_id: int) -> Admin | None:
    result = await session.execute(select(Admin).where(Admin.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def _send_login_code(message: Message, telegram_id: int) -> None:
    code = generate_login_code(telegram_id)
    await message.answer(
        f"Dashboard'ga kirish kodingiz:\n\n<code>{code}</code>\n\n"
        f"Bu kodni {settings.dashboard_origin} saytidagi kirish oynasiga kiriting. "
        "Kod 5 daqiqa amal qiladi va faqat bir marta ishlatiladi.",
        parse_mode="HTML",
    )


@main_router.message(Command("parol"))
async def cmd_password(message: Message) -> None:
    """Dashboard'ga (oddiy brauzerda) kirish uchun bir martalik kod — endi
    faqat shu komanda orqali, inline tugma olib tashlandi."""
    await _send_login_code(message, message.from_user.id)


@main_router.message(CommandStart())
async def cmd_start(
    message: Message, command: CommandObject, state: FSMContext, session: AsyncSession
) -> None:
    if command.args == "login":
        await _send_login_code(message, message.from_user.id)
        return

    admin = await _get_admin(session, message.from_user.id)

    if admin is None:
        await message.answer(
            "Assalomu alaykum! GETOLOG — yopiq Telegram kanalingiz uchun "
            "obuna boshqaruvi platformasi.\n\n"
            "Boshlash uchun to'liq ismingizni yuboring:"
        )
        await state.set_state(OnboardingStates.waiting_for_name)
        return

    # Username o'zgargan bo'lishi mumkin — har /start'da yangilab boramiz.
    if admin.username != message.from_user.username:
        admin.username = message.from_user.username
        await session.commit()

    await _retry_pending_channels(session, admin)
    await _send_start_menu(message, session, admin)


async def _send_start_menu(
    message: Message, session: AsyncSession, admin: Admin, *, edit: bool = False
) -> None:
    """Ro'yxatdan o'tgan admin uchun asosiy menyu: botlar/kanallar holati + tugmalar.

    Ham `/start`dan, ham "✅ Admin qildim" tugmasi bosilganda chaqiriladi — ikkala
    holatda ham bazadagi eng so'nggi holat (`my_chat_member` orqali jimgina
    yozib qo'yilgan) shu yerda ko'rsatiladi. Bitta bot faqat bitta kanalni
    boshqaradi — boshqa kanal kerak bo'lsa, admin yangi bot ulashi kerak
    ("➕ Bot qo'shish").

    `edit=True` bo'lsa (masalan "✅ Admin qildim" bosilganda) mavjud xabar
    tozalik uchun yangilanadi, yangi xabar qo'shilmaydi.
    """
    bots = await _get_admin_bots(session, admin.id)
    if not bots:
        text = "Xush kelibsiz, siz allaqachon ro'yxatdan o'tgansiz.\n\nBoshlash uchun birinchi botingizni ulang."
        keyboard = keyboards.start_menu_keyboard(has_bots=False)
    else:
        # Kanal/guruh limitiga yetgan admin uchun ulanmagan bot(lar)ni "hali admin
        # qilinmagan" deb emas — aslida sababi tarif limiti ekanini aniq ko'rsatamiz
        # (aks holda admin botni to'g'ri admin qilgan bo'lsa ham chalg'ituvchi
        # "hali admin qilmadingiz" xabarini ko'radi).
        at_channel_limit = not await can_add_channel(session, admin)

        lines: list[str] = []
        any_pending = False
        any_connected = False
        for bot_row in bots:
            channel_row = await _get_bot_channel(session, bot_row.id)
            if channel_row is None:
                if at_channel_limit:
                    lines.append(
                        f"⚠️ @{bot_row.username} — tarif limitiga yetdingiz, yangi kanal/guruh ulanmaydi"
                    )
                else:
                    lines.append(f"⏳ @{bot_row.username} — hali kanal/guruhga ulanmagan")
                any_pending = True
            else:
                kind = "guruh" if channel_row.chat_type == ChatType.group else "kanal"
                if not channel_row.permissions_ok:
                    lines.append(
                        f"⚠️ @{bot_row.username} — {channel_row.title} ({kind}, huquqlar yetarli emas)"
                    )
                    any_pending = True
                else:
                    lines.append(f"✅ @{bot_row.username} — {channel_row.title} ({kind})")
                    any_connected = True

        banner = ""
        if edit:
            if at_channel_limit and any_pending:
                banner = (
                    f"⚠️ Siz {TARIFF_LABELS[admin.tariff_plan]} tarifidagi kanal/guruh limitiga "
                    "yetdingiz. Yangisini ulash uchun tarifingizni oshiring — "
                    f"@{settings.support_username} ga yozing.\n\n"
                )
            elif any_pending:
                banner = (
                    "❌ Siz hali botni admin qilmadingiz. Iltimos, botni kanalingizga yoki "
                    "yopiq guruhingizga admin sifatida qo'shing.\n\n"
                )
            else:
                banner = "✅ Muvaffaqiyatli tekshirildi!\n\n"

        text = banner + "Botlaringiz:\n" + "\n".join(lines)
        if any_pending:
            text += (
                "\n\nUlanmagan botni kanalingizga yoki yopiq guruhingizga admin sifatida "
                "qo'shing (taklif qilingan barcha admin huquqlari bilan), so'ng "
                '"✅ Admin qildim" tugmasini bosing.'
            )
        if any_connected:
            text += (
                "\n\nMuhim: ulangan bot(lar)ga shaxsan /start bosing — shunda "
                "obunachilarning to'lov cheklari shu bot(lar) orqali sizga kelishi mumkin bo'ladi.\n\n"
                "Keyin dashboard orqali obunachilar uchun tarif narxlarini belgilang.\n\n"
                "Kompyuter brauzerida kirish uchun /parol buyrug'i orqali bir martalik kod oling."
            )
        keyboard = keyboards.start_menu_keyboard(has_bots=True, any_pending=any_pending)

    if edit:
        try:
            await message.edit_text(text, reply_markup=keyboard)
            return
        except TelegramAPIError:
            # Masalan matn o'zgarmagan yoki xabarni tahrirlab bo'lmaydi — yangi
            # xabar sifatida yuboramiz, foydalanuvchi baribir javob olsin.
            pass
    await message.answer(text, reply_markup=keyboard)


@main_router.callback_query(F.data == "add_bot")
async def on_add_bot_pressed(callback: CallbackQuery, state: FSMContext) -> None:
    assert isinstance(callback.message, Message)
    await callback.message.answer(
        "@BotFather orqali yangi bot yarating (/newbot) va u bergan tokenni shu yerga yuboring:"
    )
    await state.set_state(OnboardingStates.waiting_for_bot_token)
    await callback.answer()


@main_router.callback_query(F.data == "check_admin")
async def on_check_admin_pressed(callback: CallbackQuery, session: AsyncSession) -> None:
    assert isinstance(callback.message, Message)
    admin = await _get_admin(session, callback.from_user.id)
    if admin is None:
        await callback.answer()
        return
    # Limit tufayli ulanmay qolgan kanal bo'lsa — menyuni chizishdan OLDIN qayta
    # urinib ko'ramiz, shunda admin joy bo'shatgan bo'lsa shu bosishning o'zida ulanadi.
    await _retry_pending_channels(session, admin)
    await _send_start_menu(callback.message, session, admin, edit=True)
    await callback.answer()


@main_router.message(OnboardingStates.waiting_for_name, ~F.text.startswith("/"))
async def process_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    full_name = (message.text or "").strip()
    if not full_name:
        await message.answer("Iltimos, ismingizni matn ko'rinishida yuboring.")
        return

    admin = Admin(
        telegram_id=message.from_user.id,
        full_name=full_name,
        username=message.from_user.username,
        language="uz",
    )
    session.add(admin)
    await session.commit()

    await message.answer(
        f"Rahmat, {full_name}!\n\n"
        "Endi @BotFather orqali yangi bot yarating (/newbot) va u bergan "
        "tokenni shu yerga yuboring:"
    )
    await state.set_state(OnboardingStates.waiting_for_bot_token)


@main_router.message(OnboardingStates.waiting_for_bot_token, ~F.text.startswith("/"))
async def process_token(message: Message, state: FSMContext, session: AsyncSession) -> None:
    token = (message.text or "").strip()
    admin = await _get_admin(session, message.from_user.id)
    if admin is None:
        # Nazariy jihatdan bo'lmasligi kerak, lekin FSM holati saqlanib qolgan
        # bo'lsa-yu, admin yozuvi topilmasa — boshidan boshlash so'raladi.
        await message.answer("Xatolik yuz berdi, iltimos /start bosing.")
        await state.clear()
        return

    try:
        temp_bot = Bot(token=token)
        me = await temp_bot.get_me()
    except (TokenValidationError, TelegramAPIError):
        await message.answer(
            "Bu token noto'g'ri ko'rinadi. @BotFather'dan olgan tokenni "
            "to'g'ridan-to'g'ri, o'zgartirmasdan yuboring."
        )
        return
    except Exception:  # noqa: BLE001 — kutilmagan xato ham foydalanuvchiga tushunarli xabar bersin
        logger.exception("Bot tokenini tekshirishda kutilmagan xato")
        await message.answer("Xatolik yuz berdi, iltimos qayta urinib ko'ring.")
        return

    bot_row = BotModel(
        admin_id=admin.id,
        is_main=False,
        telegram_bot_id=me.id,
        token_encrypted=encrypt_token(token),
        username=me.username,
    )
    session.add(bot_row)
    await session.commit()

    registry.register_bot(temp_bot)
    webhook_url = f"{settings.webhook_base_url}/webhook/{token}"
    # Lokal import — `app.bot.dispatcher` o'zi shu modulni import qiladi
    # (`main_dp.include_router(onboarding.main_router)`), shuning uchun modul
    # darajasida import qilsak aylanma import hosil bo'lardi.
    from app.bot.dispatcher import child_dp

    await temp_bot.set_webhook(
        url=webhook_url, allowed_updates=child_dp.resolve_used_update_types()
    )

    await message.answer(
        f"Bot ulandi: @{me.username} ✅\n\n"
        "Endi shu botni kanalingizga yoki yopiq guruhingizga admin sifatida qo'shing. "
        "Unga taklif qilingan barcha huquqlarni bering (a'zolarni qo'shish/chiqarish "
        "shart; kanal bo'lsa post yuborish/o'chirish ham kerak).\n\n"
        'Qo\'shib bo\'lgach, "✅ Admin qildim" tugmasini bosing.',
        reply_markup=keyboards.start_menu_keyboard(has_bots=True, any_pending=True),
    )
    await state.clear()


async def _get_admin_bots(session: AsyncSession, admin_id: int) -> list[BotModel]:
    result = await session.execute(
        select(BotModel)
        .where(BotModel.admin_id == admin_id, BotModel.is_main.is_(False))
        .order_by(BotModel.id)
    )
    return list(result.scalars().all())


async def _get_bot_channel(session: AsyncSession, bot_id: int) -> Channel | None:
    result = await session.execute(select(Channel).where(Channel.bot_id == bot_id))
    return result.scalar_one_or_none()


async def _retry_pending_channels(session: AsyncSession, admin: Admin) -> None:
    """Tarif limiti tufayli ulanmay qolgan kanal/guruhlarni qayta ulashga urinadi.

    `/start` va "✅ Admin qildim" bosilganda chaqiriladi. Telegram `my_chat_member`
    hodisasini faqat bot statusi o'zgarganda yuboradi va "bot qaysi chatlarda
    admin" degan so'rov Bot API'da yo'q — shuning uchun rad etilgan chat ID'si
    `Bot.pending_chat_id`da saqlanadi va bu yerda Telegram'dan JONLI tekshiriladi
    (bot hali ham o'sha chatda adminmi, nomi/turi qanday).

    Admin tarifni oshirgach yoki eski kanalni o'chirgach shu funksiya ishlaydi —
    ya'ni botni kanaldan chiqarib qayta qo'shish shart emas.
    """
    for bot_row in await _get_admin_bots(session, admin.id):
        if bot_row.pending_chat_id is None:
            continue
        if await _get_bot_channel(session, bot_row.id) is not None:
            # Bot allaqachon boshqa kanalga ulangan (bitta bot — bitta kanal),
            # kutib turgan chat endi ahamiyatsiz.
            bot_row.pending_chat_id = None
            continue
        if not await can_add_channel(session, admin):
            continue  # joy hali bo'shamagan — keyingi urinishga qoldiriladi

        live_bot = registry.get_bot_by_telegram_id(bot_row.telegram_bot_id)
        if live_bot is None:
            continue

        try:
            member = await live_bot.get_chat_member(
                chat_id=bot_row.pending_chat_id, user_id=bot_row.telegram_bot_id
            )
            if not isinstance(member, ChatMemberAdministrator):
                # Bot bu chatda endi admin emas — kutishdan ma'no yo'q.
                bot_row.pending_chat_id = None
                continue
            chat = await live_bot.get_chat(bot_row.pending_chat_id)
        except TelegramAPIError:
            # Masalan chat o'chirilgan yoki bot chiqarib yuborilgan — holatni
            # buzmaymiz, keyingi bosishda yana urinib ko'riladi.
            logger.warning(
                "Kutayotgan chat %s ni tekshirib bo'lmadi (@%s)",
                bot_row.pending_chat_id,
                bot_row.username,
            )
            continue

        chat_type = ChatType.channel if chat.type == "channel" else ChatType.group
        session.add(
            Channel(
                bot_id=bot_row.id,
                telegram_channel_id=chat.id,
                title=chat.title or "",
                chat_type=chat_type,
                permissions_ok=channel_service.has_required_rights(member, chat_type),
            )
        )
        bot_row.pending_chat_id = None
        # Keyingi bot uchun `can_add_channel` shu yangi kanalni ham hisoblasin.
        await session.flush()

    await session.commit()


@child_router.my_chat_member()
async def on_bot_status_changed_in_chat(event: ChatMemberUpdated, session: AsyncSession) -> None:
    """Bot biror kanalda admin qilib qo'shilganda (yoki huquqlari o'zgarganda)
    keladi. Bu yerda faqat bazadagi holat jimgina yangilanadi — adminga xabar
    berilmaydi. Admin holatni "✅ Admin qildim" tugmasi orqali o'zi so'raydi
    (`on_check_admin_pressed` -> `_send_start_menu`).

    Bitta bot faqat bitta kanalni boshqaradi (`channels.bot_id` bazada ham
    unique): agar bot allaqachon boshqa kanalga ulangan bo'lsa, bu ikkinchi
    (boshqa) kanal e'tiborga olinmaydi — admin boshqa kanal uchun yangi bot
    ulashi kerak.
    """
    if event.chat.type not in ("channel", "group", "supergroup"):
        return
    if event.new_chat_member.status != "administrator":
        return

    result = await session.execute(
        select(BotModel).where(BotModel.telegram_bot_id == event.bot.id)
    )
    bot_row = result.scalar_one_or_none()
    if bot_row is None:
        return

    member = event.new_chat_member
    assert isinstance(member, ChatMemberAdministrator)
    chat_type = ChatType.channel if event.chat.type == "channel" else ChatType.group
    permissions_ok = channel_service.has_required_rights(member, chat_type)

    channel_row = await _get_bot_channel(session, bot_row.id)
    if channel_row is not None and channel_row.telegram_channel_id != event.chat.id:
        # Bot allaqachon boshqa kanal/guruhga ulangan — bu ikkinchisi e'tiborga olinmaydi.
        return

    if channel_row is None:
        admin_result = await session.execute(select(Admin).where(Admin.id == bot_row.admin_id))
        admin = admin_result.scalar_one()
        if not await can_add_channel(session, admin):
            # Tarif chegarasidan oshib ketadi — kanal hozircha qayd etilmaydi,
            # lekin chat ID'si ESLAB QOLINADI: admin joy bo'shatib "✅ Admin
            # qildim"ni bosganda shu ID orqali qayta urinib ko'riladi. Aks holda
            # Telegram bu hodisani boshqa yubormagani uchun admin botni kanaldan
            # chiqarib qayta qo'shishga majbur bo'lardi.
            bot_row.pending_chat_id = event.chat.id
            await session.commit()

            main_bot = registry.get_main_bot()
            try:
                await main_bot.send_message(
                    admin.telegram_id,
                    f"⚠️ Siz {TARIFF_LABELS[admin.tariff_plan]} tarifidagi kanal/guruh limitiga "
                    "yetdingiz, shuning uchun «"
                    f"{event.chat.title or 'kanal'}» hozircha ulanmadi.\n\n"
                    f"Tarifingizni oshiring (@{settings.support_username}) yoki eski "
                    'kanallardan birini o\'chiring — so\'ng "✅ Admin qildim" tugmasini '
                    "bosing, bot avtomatik ulanadi.",
                )
            except TelegramAPIError:
                pass
            return

        channel_row = Channel(
            bot_id=bot_row.id,
            telegram_channel_id=event.chat.id,
            title=event.chat.title or "",
            chat_type=chat_type,
            permissions_ok=permissions_ok,
        )
        session.add(channel_row)
        bot_row.pending_chat_id = None
    else:
        channel_row.title = event.chat.title or channel_row.title
        channel_row.chat_type = chat_type
        channel_row.permissions_ok = permissions_ok
    await session.commit()
