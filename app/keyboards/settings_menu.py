from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import *


class SettingsListCD(CallbackData, prefix="setts"): ...


class ChatListCD(CallbackData, CurrentPageArg, prefix="chat_list"): ...


class ModeratorListCD(CallbackData, CurrentPageArg, prefix="moderator_list"): ...


class DistributionListCD(CallbackData, CurrentPageArg, prefix="dist_list"): ...


class SettingsType:
    CAPTCHA = "captcha"
    WARN = "warn"


class SettingsTypeCD(CallbackData, prefix="setts_type"):
    type: str


def settings_menu_ikb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📋Чаты", callback_data=ChatListCD().pack())
    builder.button(text="👤Модераторы", callback_data=ModeratorListCD().pack())
    builder.button(
        text="✅Капча", callback_data=SettingsTypeCD(type=SettingsType.CAPTCHA).pack()
    )
    builder.button(text="💬Рассылка", callback_data=DistributionListCD().pack())
    builder.button(
        text="🚫Варны", callback_data=SettingsTypeCD(type=SettingsType.WARN).pack()
    )
    builder.adjust(*([1] * 5))

    return builder.as_markup()
