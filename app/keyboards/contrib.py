from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_paginator_ikb(page: int, callback_data_class: CallbackData, **kwargs):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='<<', callback_data=callback_data_class(page=page-1, **kwargs).pack()),
                InlineKeyboardButton(text=str(page), callback_data='#'),
                InlineKeyboardButton(text='>>', callback_data=callback_data_class(page=page+1, **kwargs).pack()),
            ]
        ]
    )
    return kb

def back_ibtn(callback_data) -> dict:
    return {
        'text':'⬅',
        'callback_data': callback_data.pack()
    }