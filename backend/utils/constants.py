# FSM States
from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    waiting_token = State()
    waiting_card = State()
    waiting_channel = State()
    waiting_price = State()
    waiting_duration = State()


class SettingsStates(StatesGroup):
    waiting_welcome = State()
    waiting_card = State()
    waiting_price = State()


class PaymentStates(StatesGroup):
    waiting_screenshot = State()


class SupportStates(StatesGroup):
    waiting_message = State()


# Duration options
DURATION_OPTIONS = {
    1: "1 oy",
    6: "6 oy",
    12: "12 oy",
    0: "Umrbod",
}

# Payment methods
PAYMENT_METHODS = {
    "card": "💳 Karta orqali",
}
