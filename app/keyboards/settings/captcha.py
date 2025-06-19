from typing import Literal

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.settings_menu import ChatListCD, SettingsListCD
from config import changeable_settings
from db.models import ChatORM


class ChangeCaptchaStatusCD(CallbackData, prefix="ch_cap_status"): ...


class ChangeCaptchaWaitingTimeActions:
    DOWN = "down"
    UP = "up"


class ChangeCaptchaWaitingTimeCD(CallbackData, prefix="ch_cap_wait_time"):
    action: Literal["down", "up"]


class ChangeCaptchaTextTypes:
    MESSAGE = "message"
    BUTTON = "button"


class ChangeCaptchaTextCD(CallbackData, prefix="ch_cap_text"):
    type: Literal["message", "button"]


def captcha_settings_ikb():
    captcha_status_text = (
        "❌ Выключить ❌" if changeable_settings.captcha_status else "✅ Включить ✅"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=captcha_status_text,
                    callback_data=ChangeCaptchaStatusCD().pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"-{changeable_settings.change_of_captcha_waiting} сек.",
                    callback_data=ChangeCaptchaWaitingTimeCD(
                        action=ChangeCaptchaWaitingTimeActions.DOWN
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=f"{changeable_settings.captcha_waitng}", callback_data="empty"
                ),
                InlineKeyboardButton(
                    text=f"+{changeable_settings.change_of_captcha_waiting} сек.",
                    callback_data=ChangeCaptchaWaitingTimeCD(
                        action=ChangeCaptchaWaitingTimeActions.UP
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="✍ Сообщение ✍",
                    callback_data=ChangeCaptchaTextCD(
                        type=ChangeCaptchaTextTypes.MESSAGE
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text="✍ Кнопку ✍",
                    callback_data=ChangeCaptchaTextCD(
                        type=ChangeCaptchaTextTypes.BUTTON
                    ).pack(),
                ),
            ],
            [InlineKeyboardButton(text="⬅", callback_data=SettingsListCD().pack())],
        ]
    )
    return kb
