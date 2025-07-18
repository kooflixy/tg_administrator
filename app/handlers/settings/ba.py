from logging import getLogger

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message
from telethon import errors, types

from app.keyboards.contrib import back_ibtn
from app.keyboards.settings_menu import SettingsListCD, SettingsType, SettingsTypeCD
from app.utils.for_logging import name_in_log
from app.utils.middleware import IsAdminChat
from app.utils.telthon_manager import TelethonManager
from config import changeable_settings, settings

log = getLogger(__name__)

router = Router()


@router.callback_query(SettingsTypeCD.filter(F.type == SettingsType.BA))
async def get_ba_settings(callback: CallbackQuery, callback_data: SettingsTypeCD):

    text = ""
    for ch, name in zip(
        [changeable_settings.ba_chat_id, changeable_settings.ba_channel_id],
        ["Чат", "Канал"],
    ):
        text += f"\n{name}:\n"
        if ch:
            id_ = str(ch)
            if id_[:4] == "-100":
                id_ = id_[4:]
            elif id_[:1] == "-":
                id_ = id_[1:]

            chat = await TelethonManager.get_entity(id_)

            if chat:
                text += f"""  <b>Название:</b> {chat.title}
  <b>ID:</b> {id_}\n"""
        else:
            text += f"  Не привязан\n"

    text += f"""
<b>Пост:</b> {changeable_settings.ba_post}

<b>Уведомление о бане:</b> {changeable_settings.ba_text}

<b>Уведомление о разбане:</b> {changeable_settings.unba_text}\n
"""

    text += "\n<code>/set_ba_chat</code> <b>[айди или ссылка на чат]</b> - изменение чата для бана по всей сети\n<code>/set_ba_channel</code> <b>[айди или ссылка на канал]</b> - изменение канала для постов о бане по всей сети\n<i>Команды для изменения текста в <code>/commands</code></i>"

    await callback.message.edit_text(
        text=text, reply_markup=back_ibtn(SettingsListCD()).as_markup()
    )


@router.message(Command("set_ba_chat"), IsAdminChat())
async def set_ba_chat(message: Message, command: CommandObject):

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
            "%s ввёл несуществующую ссылку на ba чат chat_url=%r",
            name_in_log.user(message),
            message.text,
        )
        return

    # Проверка, является ли чатом
    if isinstance(chat, types.Channel):
        if not chat.megagroup:
            await message.answer("Это не чат, а канал")
            log.info(
                "%s ввёл ссылку на ba чат, но это оказался не чат, а канал chat_url=%r",
                name_in_log.user(message),
                message.text,
            )
            return
        changeable_settings.ba_chat_id = int("-100" + str(chat.id))
    elif isinstance(chat, types.Chat):
        changeable_settings.ba_chat_id = int("-" + str(chat.id))
    else:
        await message.answer("Это не чат")
        return
    await message.answer(f"Чат для бана по сети успешно изменен на <b>{chat.title}</b>")

    log.info("id ba-чата изменено ba_chat_id=%s", changeable_settings.ba_chat_id)


@router.message(Command("set_ba_channel"), IsAdminChat())
async def set_ba_channel(message: Message, command: CommandObject):

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
        await message.answer("При попытке получить канал произошла ошибка")
        return

    if not chat:
        await message.answer("Добавить канал не удалось, попробуйте еще раз")
        log.info(
            "%s ввёл несуществующую ссылку на ba канал channel_url=%r",
            name_in_log.user(message),
            message.text,
        )
        return

    # Проверка, является ли каналом
    if isinstance(chat, types.Channel):
        if chat.megagroup:
            await message.answer("Это не канал, а чат")
            log.info(
                "%s ввёл ссылку на ba канал, но это оказался не канал, а канал channel_url=%r",
                name_in_log.user(message),
                message.text,
            )
            return
        changeable_settings.ba_channel_id = int("-100" + str(chat.id))

    await message.answer(
        f"Канал для бана по сети успешно изменен на <b>{chat.title}</b>"
    )

    log.info(
        "id ba-канала изменено ba_channel_id=%s", changeable_settings.ba_channel_id
    )
