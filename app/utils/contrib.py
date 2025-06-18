import asyncio
from dataclasses import dataclass
from typing import Optional
from aiogram.types import Message
from aiogram.filters import CommandObject
import re

from app.contrib.telthon_manager import TelethonManager
from app.bot_obj import bot


def time_text_to_seconds(text):
    units = {
        # секунды
        'секунда': 1, 'секунды': 1, 'секунд': 1, 'с': 1,
        # минуты
        'минута': 60, 'минуты': 60, 'минут': 60, 'мин': 60,
        # часы
        'час': 3600, 'часа': 3600, 'часов': 3600, 'ч': 3600,
        # дни
        'день': 86400, 'дня': 86400, 'дней': 86400, 'дн': 86400,
        # месяцы (условно 30 дней)
        'месяц': 2592000, 'месяца': 2592000, 'месяцев': 2592000,
    }

    # Поиск всех пар "число + единица"
    matches = re.findall(r'(\d+)\s*([а-яА-ЯёЁ]+)', text.lower())

    total_seconds = 0
    for value, unit in matches:
        seconds = units.get(unit)
        if seconds:
            total_seconds += int(value) * seconds

    return total_seconds

class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

async def get_user_id_name(message: Message, command: CommandObject) -> Optional[User]:
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name

        user = User(id=user_id, name=user_name)
    else:
        if not command.args: return

        tl_user = await TelethonManager.get_user(command.args)
        if not tl_user:
            msg = await message.reply('Такого пользователя не существует')
            await asyncio.sleep(10)
            await bot.delete_messages(message.chat.id, [msg.message_id, message.message_id])
            return

        user = User(id=tl_user.id, name=TelethonManager.get_full_name(tl_user))

    return user