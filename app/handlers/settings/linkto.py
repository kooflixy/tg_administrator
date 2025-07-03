from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from telethon import errors, types

from app.utils.for_logging import name_in_log
from app.utils.telthon_manager import TelethonManager
from config import changeable_settings, settings

log = getLogger(__name__)

router = Router()


@router.message(Command("set_linkto_chat"))
async def set_linkto_chat(message: Message, command: CommandObject):

    # Проверка, является ли пользователь главным админом
    if message.chat.id != settings.ADMIN_ID:
        return

    if not command.args:
        return

    id_ = command.args
    if id_[:4] == "-100":
        id_ = id_[:4]

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

    # Проверка, на тип: является ли чатом или группой
    if not isinstance(chat, types.Channel):
        await message.answer("Это не чат")
        log.info(
            "%s ввёл ссылку на linkto чат, но это оказался не чат chat_url=%r",
            name_in_log.user(message),
            message.text,
        )
        return

    # Проверка, является ли чатом
    if not chat.megagroup:
        await message.answer("Это не чат, а канал")
        log.info(
            "%s ввёл ссылку на linkto чат, но это оказался не чат, а канал chat_url=%r",
            name_in_log.user(message),
            message.text,
        )
        return

    changeable_settings.linkto_chat_id = chat.id

    await message.answer(f"Чат для линковки успешно изменен на <b>{chat.title}</b>")

    log.info("id linkto-чата изменено linkto_chat_id=%s", chat.id)
