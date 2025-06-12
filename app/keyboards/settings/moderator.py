from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.keyboards.settings_menu import ModeratorListCD, SettingsListCD
from db.models import ModeratorORM

class AddModeratorCD(CallbackData, prefix='add_moderator'): ...

class RemoveModeratorCD(CallbackData, prefix='remove_moderator'):
    moderator_id: int
    page: int

class ModeratorDetailsCD(CallbackData, prefix='moderator_d'):
    moderator_id: int
    page: int

def moderator_list_ikb(moderator_list: list[ModeratorORM], page: int):
    # Создание клавиатуры кнопок
    button_list = []
    button_list.append([InlineKeyboardButton(text='Добавить модератора', callback_data=AddModeratorCD().pack())])
    for moderator in moderator_list:
        btn = InlineKeyboardButton(text=moderator.name, callback_data=ModeratorDetailsCD(moderator_id=moderator.id, page=page).pack())
        button_list.append([btn])
    button_list.append([
        InlineKeyboardButton(text='⬅', callback_data=SettingsListCD().pack()),
        InlineKeyboardButton(text='<<', callback_data=ModeratorListCD(page=page-1).pack()),
        InlineKeyboardButton(text=str(page), callback_data='empty'),
        InlineKeyboardButton(text='>>', callback_data=ModeratorListCD(page=page+1).pack()),
    ])

    kb = InlineKeyboardMarkup(
        inline_keyboard=button_list
    )
    return kb