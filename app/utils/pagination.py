from typing import Literal

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class pag_act:
    PREV = "prev"
    NEXT = "next"


class Paginator(CallbackData, prefix="#"):
    page: int
    action: Literal["prev", "next"]


class FirstPageErrCD(CallbackData, prefix="first_page_err"): ...


class LastPageErrCD(CallbackData, prefix="last_page_err"): ...


class ShowYourPageCD(CallbackData, prefix="show_your_page"): ...


def get_paginator_ikb(
    callback_data_cls: CallbackData, *, cur_page: int = 1, is_last_page: bool, **kwargs
):
    builder = InlineKeyboardBuilder()

    if cur_page <= 1:
        builder.button(text="⏪", callback_data=FirstPageErrCD().pack())
    else:
        builder.button(
            text="⏪",
            callback_data=callback_data_cls(cur_page=cur_page - 1, **kwargs).pack(),
        )

    builder.button(text=str(cur_page), callback_data=ShowYourPageCD().pack())

    if is_last_page:
        builder.button(text="⏩", callback_data=LastPageErrCD().pack())
    else:
        builder.button(
            text="⏩",
            callback_data=callback_data_cls(cur_page=cur_page + 1, **kwargs).pack(),
        )

    return builder
