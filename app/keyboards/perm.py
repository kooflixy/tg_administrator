from dataclasses import dataclass
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import *
from app.utils.pagination import get_paginator_ikb
from app.utils.perm import permissions_translations, redistribute_dict
from db.models import ChatORM, ModeratorChatORM, ModeratorORM


class ChangePermCD(
    CallbackData, UserIdArg, ChatIDArg, PermNameArg, prefix="ch_u_p"
): ...


class ResetPermCD(CallbackData, UserIdArg, ChatIDArg, prefix="res_p"): ...


def get_emoji(a: bool):
    if a:
        return "✅"
    return "❌"


def get_perm_list_ikb(perms: dict, chat_id: int, user_id: Optional[int] = None):
    builder = InlineKeyboardBuilder()

    perms = redistribute_dict(perms)
    for perm in perms.keys():
        emoji = get_emoji(perms[perm])
        ru_perm = permissions_translations[perm]
        builder.button(
            text=emoji + ru_perm,
            callback_data=ChangePermCD(
                perm=perm, chat_id=chat_id, user_id=user_id
            ).pack(),
        )
    builder.button(
        text="🔁Сбросить",
        callback_data=ResetPermCD(chat_id=chat_id, user_id=user_id).pack(),
    )
    builder.adjust(*([2] * 7), 1)
    return builder.as_markup()
