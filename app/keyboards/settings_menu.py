from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class SettingsType:
    CAPTCHA = 'captcha'

class SettingsTypeCD(CallbackData, prefix='setts_type'):
    type: str

class SettingsListCD(CallbackData, prefix='setts'): ...

class ChatListCD(CallbackData, prefix='chat_list'):
    page: int = 1

class ModeratorListCD(CallbackData, prefix='moderator_list'):
    page: int = 1

def settings_menu_ikb():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📋Чаты', callback_data=ChatListCD().pack())],
            [InlineKeyboardButton(text='👤Модераторы', callback_data=ModeratorListCD().pack())],
            [InlineKeyboardButton(text='✅Капча', callback_data=SettingsTypeCD(type=SettingsType.CAPTCHA).pack())],
        ]
    )
    return kb
