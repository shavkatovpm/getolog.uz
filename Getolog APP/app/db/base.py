"""Ma'lumotlar bazasiga ulanish uchun asosiy sozlamalar."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Barcha jadval modellari (app/db/models.py) shu klassdan meros oladi."""


engine = create_async_engine(settings.database_url, echo=False)

# Har bir so'rov/handler uchun yangi sessiya ochish uchun ishlatiladi
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Bitta DB sessiyasini ochib beradi, ish tugagach avtomatik yopadi."""
    async with async_session_factory() as session:
        yield session
