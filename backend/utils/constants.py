# FSM States
from enum import StrEnum

from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    waiting_token = State()
    waiting_card = State()
    waiting_channel = State()
    waiting_channel_manual = State()
    waiting_price = State()
    waiting_duration = State()


class SettingsStates(StatesGroup):
    waiting_welcome = State()
    waiting_card = State()
    waiting_price = State()
    waiting_collab_id = State()


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


class PaymentStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PlanName(StrEnum):
    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"


class SubStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    KICKED = "kicked"
