from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.settings_menu import ChatListCD
from db.models import ChatORM

class AddChatCD(CallbackData, prefix='add_chat'): ...

class ChatInfoCD(CallbackData, prefix='chat_i'):
    chat_id: int

def chat_list_ikb(chat_list: list[ChatORM], page: int):
    button_list = []
    button_list.append([InlineKeyboardButton(text='Добавить чат', callback_data=AddChatCD().pack())])
    for chat in chat_list:
        btn = InlineKeyboardButton(text=chat.name, callback_data=ChatInfoCD(chat_id=chat.id).pack())
        button_list.append([btn])
    button_list.append([
        InlineKeyboardButton(text='<<', callback_data=ChatListCD(page=page-1).pack()),
        InlineKeyboardButton(text='>>', callback_data=ChatListCD(page=page+1).pack())
    ])

    kb = InlineKeyboardMarkup(
        inline_keyboard=button_list
    )
    return kb