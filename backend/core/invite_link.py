from aiogram import Bot


async def create_invite_link(bot: Bot, chat_id: int) -> str:
    """Create a one-time invite link for a channel/group."""
    link = await bot.create_chat_invite_link(
        chat_id=chat_id,
        member_limit=1,
        name="Getolog auto-invite",
    )
    return link.invite_link


async def kick_member(bot: Bot, chat_id: int, user_id: int) -> bool:
    """Remove a user from channel/group when subscription expires."""
    try:
        await bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
        return True
    except Exception:
        return False
