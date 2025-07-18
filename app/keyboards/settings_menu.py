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
    LINKTO = "linkto"
    BA = "ba"
    LOCAL = "local"


class SettingsTypeCD(CallbackData, prefix="setts_type"):
    type: str


BTN_COUNT = 6


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
    builder.button(
        text="🔀Линковка", callback_data=SettingsTypeCD(type=SettingsType.LINKTO).pack()
    )
    builder.button(
        text="😈Ба",
        callback_data=SettingsTypeCD(type=SettingsType.BA).pack(),
    )
    builder.button(
        text="🤫Локал",
        callback_data=SettingsTypeCD(type=SettingsType.LOCAL).pack(),
    )

    builder.adjust(*([1] * (BTN_COUNT % 2) + [2] * (BTN_COUNT // 2)))

    return builder.as_markup()
