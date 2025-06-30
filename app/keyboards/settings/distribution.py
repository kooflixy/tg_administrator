from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import *
from app.keyboards.contrib import back_ibtn
from app.keyboards.settings_menu import DistributionListCD, SettingsListCD
from app.utils.pagination import get_paginator_ikb
from db.models import DistributionORM


class DistributionDetailsCD(CallbackData, DistIdArg, BackPageArg, prefix="dist_d"): ...


def distribution_list_ikb(
    dist_list: list[DistributionORM], page: int, is_last_page: bool
):
    builder = InlineKeyboardBuilder()
    for dist in dist_list:
        builder.button(
            text=dist.name,
            callback_data=DistributionDetailsCD(dist_id=dist.id, back_page=page).pack(),
        )
    builder.attach(
        get_paginator_ikb(DistributionListCD, cur_page=page, is_last_page=is_last_page)
    )
    builder.attach(back_ibtn(SettingsListCD()))

    return builder.as_markup()
