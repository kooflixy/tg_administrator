from logging import getLogger

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart, or_f
from aiogram.types import CallbackQuery, Message

from app.keyboards.settings_menu import SettingsListCD, settings_menu_ikb
from app.keyboards.user_commands import menu_rkb
from app.utils.for_logging import name_in_log
from config import settings

log = getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start(message: Message):

    # Проверка, является ли пользователь главным админом
    if message.chat.id != settings.ADMIN_ID:
        return

    await message.answer(
        "Привет! Это твой бот для управления чатами:)", reply_markup=menu_rkb
    )

    log.info("Старт бота в чате с админом")


@router.message(
    or_f(Command("settings"), F.text.casefold().in_(["⚙настройки", "настройки"]))
)
async def settings_cmd(message: Message):
    log.debug("%s запросил настройки бота", name_in_log.user(message))

    # Проверка, является ли пользователь главным админом
    if message.chat.id != settings.ADMIN_ID:
        return

    await message.answer(
        f"Вот список настроек бота, {message.from_user.full_name}",
        reply_markup=settings_menu_ikb(),
    )
    log.info("%s получил настройки бота", name_in_log.user(message))


@router.callback_query(SettingsListCD.filter())
async def settings_cmd_cq(callback: CallbackQuery):
    log.debug(
        "%s запросил настройки бота через инлайн-кнопку", name_in_log.user(callback)
    )

    await callback.message.edit_text(
        f"Вот список настроек бота, {callback.from_user.full_name}",
        reply_markup=settings_menu_ikb(),
    )

    log.info(
        "%s получил настройки бота, запрошенные через инлайн-кнопку",
        name_in_log.user(callback),
    )


@router.message(
    or_f(
        Command("commands_list"),
        F.text.casefold().in_(["📋список команд", "список команд", "команды"]),
    )
)
async def get_commands_list(message: Message):

    # Проверка, является ли пользователь главным админом
    if message.chat.id != settings.ADMIN_ID:
        return

    text = """
🌟<b>Команды для изменения текста:</b>

<code>/set_close_text</code> <b>[новый текст сообщения]</b> - изменение текста сообщения при закрытии чата

<code>/set_already_close_text</code> <b>[новый текст сообщения]</b> - изменение текста сообщения при попытке закрыть уже закрытый чат

<code>/set_open_text</code> <b>[новый текст сообщения]</b> - изменение текста сообщения при открытии чата

<code>/set_already_open_text</code> <b>[новый текст сообщения]</b> - изменение текста сообщения при попытке открыть уже открытый чата


💬<b>Команды для управления рассылками:<b>

<code>/add_dist</code> <b>[интервал]</b> - добавление рассылки(пишите ответом на сообщение рассылки)

<code>/set_dist_int</code> <b>[id рассылки]</b> <b>[интервал]</b> - изменение интервала рассылки(id берется из деталей рассылки)
"""

    await message.answer(text)

    log.info("Был запрошен список команд")
