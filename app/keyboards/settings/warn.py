from dataclasses import dataclass
from typing import Literal

from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.keyboards.contrib import back_ibtn
from app.keyboards.settings_menu import SettingsListCD, SettingsType, SettingsTypeCD
from config import changeable_settings
from db.classes import ActionTypeEnum

CHANGE_OF_MUTE_TIME = 1
"""В днях"""


class ChangeWarnActions:
    DOWN = "down"
    UP = "up"


@dataclass
class ActionTypeArg:
    action: Literal["down", "up"]


class ChangeWarnLimitCD(CallbackData, ActionTypeArg, prefix="ch_warn_limit"): ...


class ChangeWarnExcessMuteTimeCD(
    CallbackData, ActionTypeArg, prefix="ch_warn_ex_m_t"
): ...


class ChangeWarnExcessRestCD(CallbackData, prefix="change_warn_rest"):
    rest_name: str
    """Ограничение, на которое будет меняться наказание"""


def warn_setts_ikb():
    """Создание инлайн-клавиатуры со списокм настроек варнов
    Кнопки: настройки кол-ва варнов; наказание за превышение; настройки длительности мута(если наказание - мут); назад(в настройки бота)
    Появляется при: выборе в списке настроек бота
    """

    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"-1", callback_data=ChangeWarnLimitCD(action=ChangeWarnActions.DOWN)
    )
    builder.button(text=str(changeable_settings.max_warn_count), callback_data="empty")
    builder.button(
        text=f"+1", callback_data=ChangeWarnLimitCD(action=ChangeWarnActions.UP)
    )

    if changeable_settings.max_warn_restriction.value == ActionTypeEnum.BAN.value:
        builder.button(
            text="🚫 Бан 🚫",
            callback_data=ChangeWarnExcessRestCD(rest_name=ActionTypeEnum.MUTE.value),
        )

        builder.attach(back_ibtn(SettingsListCD()))
        builder.adjust(3, 1, 1)
    elif changeable_settings.max_warn_restriction.value == ActionTypeEnum.MUTE.value:
        builder.button(
            text="🔇 Мут 🔇",
            callback_data=ChangeWarnExcessRestCD(rest_name=ActionTypeEnum.BAN.value),
        )

        builder.button(
            text=f"-{CHANGE_OF_MUTE_TIME} дн.",
            callback_data=ChangeWarnExcessMuteTimeCD(action=ChangeWarnActions.DOWN),
        )
        builder.button(
            text=f"{changeable_settings.max_warn_mute_time} дн.", callback_data="empty"
        )
        builder.button(
            text=f"+{CHANGE_OF_MUTE_TIME} дн.",
            callback_data=ChangeWarnExcessMuteTimeCD(action=ChangeWarnActions.UP),
        )
        builder.attach(back_ibtn(SettingsListCD()))
        builder.adjust(3, 1, 3, 1)

    return builder.as_markup()
