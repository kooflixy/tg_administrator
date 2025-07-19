from logging import getLogger

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.utils.checkers import RestChecker
from app.utils.middleware import ChatTypeFilter

log = getLogger(__name__)

router = Router()

MESSAGE_TEXT = "Сделано @kooflixy"


@router.message(Command("developer"), ChatTypeFilter("private"))
async def get_developer_info_private(message: Message, command: CommandObject):
    await message.answer(MESSAGE_TEXT)


@router.message(Command("developer"), ChatTypeFilter(["group", "supergroup"]))
async def get_developer_info_public(message: Message, command: CommandObject):
    await RestChecker.reply_n_delete(MESSAGE_TEXT, message, interval=10)
