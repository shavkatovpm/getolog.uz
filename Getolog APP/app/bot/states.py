"""FSM (holat mashinasi) bosqichlari — foydalanuvchidan ketma-ket ma'lumot so'rashda ishlatiladi."""

from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """Bosh botda yangi admin ro'yxatdan o'tish bosqichlari."""

    waiting_for_name = State()
    waiting_for_bot_token = State()


class SubscriberPaymentStates(StatesGroup):
    """Obunachi to'lov chekini yuborish bosqichi."""

    waiting_for_receipt = State()
