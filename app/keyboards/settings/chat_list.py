from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.settings_menu import ChatListCD, SettingsListCD
from db.models import ChatORM

class AddChatCD(CallbackData, prefix='add_chat'): ...

class RemoveChatCD(CallbackData, prefix='remove_chat'):
    chat_id: int
    page: int

class ChatDetailsCD(CallbackData, prefix='chat_d'):
    chat_id: int
    page: int

def chat_list_ikb(chat_list: list[ChatORM], page: int):
    # Создание клавиатуры кнопок
    button_list = []
    button_list.append([InlineKeyboardButton(text='Добавить чат', callback_data=AddChatCD().pack())])
    for chat in chat_list:
        btn = InlineKeyboardButton(text=chat.name, callback_data=ChatDetailsCD(chat_id=chat.id, page=page).pack())
        button_list.append([btn])
    button_list.append([
        InlineKeyboardButton(text='⬅', callback_data=SettingsListCD().pack()),
        InlineKeyboardButton(text='<<', callback_data=ChatListCD(page=page-1).pack()),
        InlineKeyboardButton(text=str(page), callback_data='empty'),
        InlineKeyboardButton(text='>>', callback_data=ChatListCD(page=page+1).pack()),
    ])

    kb = InlineKeyboardMarkup(
        inline_keyboard=button_list
    )
    return kb

def chat_details_ikb(chat_id: int, page: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='❌Удалить', callback_data=RemoveChatCD(chat_id=chat_id, page=page).pack())],
            [InlineKeyboardButton(text='⬅', callback_data=ChatListCD(page=page).pack())],
        ]
    )
    return kb

def removed_chat_details_ikb(page: int):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='⬅', callback_data=ChatListCD(page=page).pack())],
        ]
    )
    return kb