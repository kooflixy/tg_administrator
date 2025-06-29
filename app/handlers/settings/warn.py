from logging import getLogger

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.handlers.user_commands import settings_cmd
from app.keyboards.settings.captcha import *
from app.keyboards.settings.warn import (
    CHANGE_OF_MUTE_TIME,
    ChangeWarnActions,
    ChangeWarnExcessMuteTimeCD,
    ChangeWarnExcessRestCD,
    ChangeWarnLimitCD,
    warn_setts_ikb,
)
from app.keyboards.settings_menu import SettingsType, SettingsTypeCD
from app.utils.for_logging import name_in_log
from app.utils.states import ChangeCaptchaTextForm
from config import changeable_settings
from db.classes import ActionTypeEnum

log = getLogger(__name__)

router = Router()


@router.callback_query(SettingsTypeCD.filter(F.type == SettingsType.WARN))
async def warn_settings(callback: CallbackQuery, callback_data: SettingsTypeCD):
    log.debug(
        "Попытка запросить список настроек варнов moderator=%s",
        name_in_log.user(callback),
    )

    if changeable_settings.max_warn_restriction.value == ActionTypeEnum.BAN.value:
        rest_str = "Бан"
        time_str = ""
    elif changeable_settings.max_warn_restriction.value == ActionTypeEnum.MUTE.value:
        rest_str = "Мут"
        time_str = (
            f"<b>🔇Длительность мута:</b> {changeable_settings.max_warn_mute_time} дн."
        )

    await callback.message.edit_text(
        text=f"""
<b>⚙Лимит варнов:</b> {changeable_settings.max_warn_count}
<b>🥺Наказание:</b> {rest_str}
{time_str}
""",
        reply_markup=warn_setts_ikb(),
    )

    log.debug("Получил список настроек варнов moderator=%s", name_in_log.user(callback))


@router.callback_query(ChangeWarnLimitCD.filter())
async def change_warn_limit(callback: CallbackQuery, callback_data: ChangeWarnLimitCD):
    log.debug(
        "Попытка изменить лимит варнов moderator=%s warn_max_count_before=%s",
        name_in_log.user(callback),
        changeable_settings.max_warn_count,
    )

    if callback_data.action == ChangeWarnActions.DOWN:
        if changeable_settings.max_warn_count - 1 < 1:
            await callback.answer("Количество не может быть меньше единицы(")
            return
        changeable_settings.max_warn_count -= 1
    else:
        changeable_settings.max_warn_count += 1

    log.info(
        "Изменение лимита варнов moderator=%s warn_max_count_after=%s",
        name_in_log.user(callback),
        changeable_settings.max_warn_count,
    )
    await warn_settings(callback, None)


@router.callback_query(ChangeWarnExcessRestCD.filter())
async def change_warn_rest(
    callback: CallbackQuery, callback_data: ChangeWarnExcessRestCD
):
    log.debug(
        "Попытка изменить наказание за превышение лимита варнов moderator=%s max_warn_restriction_before=%s",
        name_in_log.user(callback),
        changeable_settings.max_warn_restriction,
    )

    changeable_settings.max_warn_restriction = ActionTypeEnum._value2member_map_[
        callback_data.rest_name
    ]

    log.info(
        "Изменение наказания за превышение лимита варнов moderator=%s max_warn_restriction_after=%s",
        name_in_log.user(callback),
        changeable_settings.max_warn_restriction,
    )
    await warn_settings(callback, None)


@router.callback_query(ChangeWarnExcessMuteTimeCD.filter())
async def change_warn_excess_time(
    callback: CallbackQuery, callback_data: ChangeWarnExcessMuteTimeCD
):
    log.debug(
        "Попытка изменить длительность мута за превышение лимита варнов moderator=%s max_warn_mute_time_before=%s",
        name_in_log.user(callback),
        changeable_settings.max_warn_mute_time,
    )
    if callback_data.action == ChangeWarnActions.DOWN:
        if changeable_settings.max_warn_mute_time - CHANGE_OF_MUTE_TIME < 1:
            await callback.answer("Длительность мута не может быть меньше единицы(")
            return
        changeable_settings.max_warn_mute_time -= CHANGE_OF_MUTE_TIME
    else:
        changeable_settings.max_warn_mute_time += CHANGE_OF_MUTE_TIME

    log.info(
        "Изменение длительности мута за превышение лимита варнов moderator=%s max_warn_mute_time_after=%s",
        name_in_log.user(callback),
        changeable_settings.max_warn_mute_time,
    )
    await warn_settings(callback, None)
