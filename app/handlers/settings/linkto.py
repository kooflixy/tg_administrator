from logging import getLogger

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message
from telethon import errors, types

from app.keyboards.contrib import back_ibtn
from app.keyboards.settings_menu import SettingsListCD, SettingsType, SettingsTypeCD
from app.utils.for_logging import name_in_log
from app.utils.telthon_manager import TelethonManager
from config import changeable_settings, settings

log = getLogger(__name__)

router = Router()


@router.callback_query(SettingsTypeCD.filter(F.type == SettingsType.LINKTO))
async def get_linkto_settings(callback: CallbackQuery, callback_data: SettingsTypeCD):
    id_ = (
        str(changeable_settings.linkto_chat_id)
        if changeable_settings.linkto_chat_id
        else changeable_settings.linkto_chat_id
    )
    if id_:
        if id_[:4] == "-100":
            id_ = id_[4:]
        elif id_[:1] == "-":
            id_ = id_[1:]

        chat = await TelethonManager.get_entity(id_)

        if not chat:
            text = f"Такого чата не существует\n<b>ID:</b> {id_}"
        else:
            text = f"""
<b>Название:</b> {chat.title}
<b>ID:</b> {id_}"""
    else:
        text = "Чат для линковки еще не привязан"

    text += "\n\n<code>/set_linkto_chat</code> <b>[айди или ссылка на чат]</b> - изменение чата для линковки"

    await callback.message.edit_text(
        text=text, reply_markup=back_ibtn(SettingsListCD()).as_markup()
    )


@router.message(Command("set_linkto_chat"))
async def set_linkto_chat(message: Message, command: CommandObject):

    # Проверка, является ли пользователь главным админом
    if message.chat.id != settings.ADMIN_ID:
        return

    if not command.args:
        return

    id_ = command.args
    if id_[:4] == "-100":
        id_ = id_[4:]

    try:
        chat = await TelethonManager.get_entity(id_)
    except errors.BotMethodInvalidError:
        await message.answer(
            f'Вы пытаетесь добавить приватный чат. Попробуйте вместо ссылки ввести id чата.\n<a href="https://t.me/username_to_id_bot">получить id можно здесь</a>'
        )
        return
    except:
        await message.answer("При попытке получить чат произошла ошибка")
        return

    if not chat:
        await message.answer("Добавить чат не удалось, попробуйте еще раз")
        log.info(
            "%s ввёл несуществующую ссылку на linkto чат chat_url=%r",
            name_in_log.user(message),
            message.text,
        )
        return

    # Проверка, является ли чатом
    if isinstance(chat, types.Channel):
        if not chat.megagroup:
            await message.answer("Это не чат, а канал")
            log.info(
                "%s ввёл ссылку на linkto чат, но это оказался не чат, а канал chat_url=%r",
                name_in_log.user(message),
                message.text,
            )
            return
        changeable_settings.linkto_chat_id = int("-100" + str(chat.id))
    elif isinstance(chat, types.Chat):
        changeable_settings.linkto_chat_id = int("-" + str(chat.id))
    else:
        await message.answer("Это не чат")
        return
    await message.answer(f"Чат для линковки успешно изменен на <b>{chat.title}</b>")

    log.info(
        "id linkto-чата изменено linkto_chat_id=%s", changeable_settings.linkto_chat_id
    )
