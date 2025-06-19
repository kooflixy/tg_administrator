from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.contrib import *


class SettingsListCD(CallbackData, prefix="setts"): ...


class ChatListCD(CallbackData, CurrentPageArg, prefix="chat_list"): ...


class ModeratorListCD(CallbackData, CurrentPageArg, prefix="moderator_list"): ...


class SettingsType:
    CAPTCHA = "captcha"


class SettingsTypeCD(CallbackData, prefix="setts_type"):
    type: str


def settings_menu_ikb():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋Чаты", callback_data=ChatListCD().pack())],
            [
                InlineKeyboardButton(
                    text="👤Модераторы", callback_data=ModeratorListCD().pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅Капча",
                    callback_data=SettingsTypeCD(type=SettingsType.CAPTCHA).pack(),
                )
            ],
        ]
    )
    return kb
