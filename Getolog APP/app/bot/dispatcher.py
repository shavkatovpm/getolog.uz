"""Ikkita mustaqil Dispatcher: biri GETOLOG bosh boti, biri adminlarning
shaxsiy botlari uchun. Har biri faqat o'ziga tegishli routerlarni ishlatadi.

Bosh bot faqat onboarding uchun ishlatiladi (admin ismini so'raydi, bot
tokenini oladi, kanalga ulanishini kuzatadi) — boshqaruv (tarif, narx,
to'lovlarni tasdiqlash) endi dashboard (`app/api`) orqali amalga oshadi.
Admin boti esa faqat obunachilar bilan ishlaydi.
"""

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import onboarding, subscriber_flow
from app.bot.middlewares import DbSessionMiddleware

main_dp = Dispatcher(storage=MemoryStorage())
main_dp.update.middleware(DbSessionMiddleware())
main_dp.include_router(onboarding.main_router)

child_dp = Dispatcher(storage=MemoryStorage())
child_dp.update.middleware(DbSessionMiddleware())
child_dp.include_router(onboarding.child_router)
child_dp.include_router(subscriber_flow.router)
