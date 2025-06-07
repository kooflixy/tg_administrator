from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class SettingsType:
    CHATS = 'chats'

class SettingsTypeCD(CallbackData, prefix='setts_type'):
    type: str

class ChatListCD(CallbackData, prefix='chat_list'):
    page: int = 1

def settings_menu_ikb():
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='📋Чаты', callback_data=ChatListCD(page=1).pack())]
        ]
    )
    return kb