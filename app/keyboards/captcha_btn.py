from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import changeable_settings


class CaptchaPassedCD(CallbackData, prefix="captcha_passed"):
    user_id: int
    captcha_msg_id: int


def captcha_btn_ikb(user_id: int, captcha_msg_id: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=changeable_settings.captcha_button_text,
                    callback_data=CaptchaPassedCD(
                        user_id=user_id, captcha_msg_id=captcha_msg_id
                    ).pack(),
                )
            ]
        ]
    )
    return kb
