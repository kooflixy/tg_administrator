from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.utils.middleware import IsAdminChat
from config import changeable_settings, settings

log = getLogger(__name__)

router = Router()


@router.message(Command("set_close_text"), IsAdminChat())
async def set_close_text(message: Message, command: CommandObject):

    changeable_settings.close_text = command.args

    await message.answer(f"Сообщение при закрытии чата изменено на:\n{command.args}")

    log.info("Текст при закрытии чата изменен new_text=%r", command.args)


@router.message(Command("set_already_close_text"), IsAdminChat())
async def set_close_text(message: Message, command: CommandObject):

    changeable_settings.already_close_text = command.args

    await message.answer(
        f"Сообщение при попытке закрыть уже закрытый чат изменено на:\n{command.args}"
    )

    log.info(
        "Текст при попытке закрыть уже закрытый чат изменен new_text=%r", command.args
    )


@router.message(Command("set_open_text"), IsAdminChat())
async def set_open_text(message: Message, command: CommandObject):

    changeable_settings.open_text = command.args

    await message.answer(f"Сообщение при открытии чата изменено на:\n{command.args}")

    log.info("Текст при открытии чата изменен new_text=%r", command.args)


@router.message(Command("set_already_open_text"), IsAdminChat())
async def set_close_text(message: Message, command: CommandObject):

    changeable_settings.already_open_text = command.args

    await message.answer(
        f"Сообщение при попытке открыть уже откырытый чат изменено на:\n{command.args}"
    )

    log.info(
        "Текст при попытке открыть уже откырытый чат изменен new_text=%r", command.args
    )


@router.message(Command("set_ba_post"), IsAdminChat())
async def set_ba_post(message: Message, command: CommandObject):

    changeable_settings.ba_post = command.args

    await message.answer(f"Пост в канал о бане по сети изменен на:\n{command.args}")

    log.info("Пост в канал о бане по сети изменен new_text=%r", command.args)


@router.message(Command("set_ba_text"), IsAdminChat())
async def set_ba_text(message: Message, command: CommandObject):

    changeable_settings.ba_text = command.args

    await message.answer(f"Уведомление о бане по сети изменено на:\n{command.args}")

    log.info("Уведомление о бане по сети изменено на new_text=%r", command.args)


@router.message(Command("set_unba_text"), IsAdminChat())
async def set_unba_text(message: Message, command: CommandObject):

    changeable_settings.unba_text = command.args

    await message.answer(f"Уведомление о разбане по сети изменено на:\n{command.args}")

    log.info("Уведомление о разбане по сети изменено на new_text=%r", command.args)
