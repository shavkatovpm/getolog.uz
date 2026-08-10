"""Ikkita mustaqil Dispatcher: biri GETOLOG bosh boti, biri adminlarning
shaxsiy botlari uchun. Har biri faqat o'ziga tegishli routerlarni ishlatadi.

Bosh bot onboarding (admin ismini so'raydi, bot tokenini oladi, kanalga
ulanishini kuzatadi) hamda to'lovlarni tezkor tasdiqlash/rad etish
(`payment_review`) uchun ishlatiladi — asosiy boshqaruv (tarif, narx) dashboard
(`app/api`) orqali amalga oshadi. Admin boti esa faqat obunachilar bilan ishlaydi.
"""

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.handlers import onboarding, payment_review, subscriber_flow
from app.bot.middlewares import DbSessionMiddleware

main_dp = Dispatcher(storage=MemoryStorage())
main_dp.update.middleware(DbSessionMiddleware())
main_dp.include_router(onboarding.main_router)
main_dp.include_router(payment_review.router)

child_dp = Dispatcher(storage=MemoryStorage())
child_dp.update.middleware(DbSessionMiddleware())
child_dp.include_router(onboarding.child_router)
child_dp.include_router(subscriber_flow.router)
