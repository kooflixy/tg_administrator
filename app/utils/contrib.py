import asyncio
from dataclasses import dataclass
from logging import getLogger
from typing import Optional
from aiogram.types import Message
from aiogram.filters import CommandObject
import re

from app.contrib.telthon_manager import TelethonManager
from app.bot_obj import bot

BAN_FOREVER = 40_000_000

log = getLogger(__name__)

# fmt: off
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
# fmt: on


def time_text_to_seconds(text):

    if not isinstance(text, str) or not text.strip():
        return None  # Пустой или нестроковый ввод

    matches = re.findall(r"(\d+)\s*([а-яА-ЯёЁ]+)", text.lower())

    if not matches:
        return None  # Нет валидных пар число + единица

    total_seconds = 0
    for value, unit in matches:
        seconds = units.get(unit)
        if not seconds:
            return None  # Неизвестная единица измерения
        total_seconds += int(value) * seconds

    return total_seconds if total_seconds > 0 else None


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
        if not command.args:
            return

        tl_user = await TelethonManager.get_user(command.args)
        if not tl_user:
            msg = await message.reply("Такого пользователя не существует")
            await asyncio.sleep(10)
            await bot.delete_messages(
                message.chat.id, [msg.message_id, message.message_id]
            )
            return

        user = User(id=tl_user.id, name=TelethonManager.get_full_name(tl_user))

    return user


async def get_user_id_name_period(
    message: Message, command: CommandObject
) -> tuple[Optional[User], Optional[int]]:
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name

        user = User(id=user_id, name=user_name)

        if not command.args:
            log.debug('Попытка получить данные для мута: is_replied=%r', message.reply_to_message)
            return user, BAN_FOREVER

        period = time_text_to_seconds(command.args)

    else:
        if not command.args:
            return None, None

        # message.entities[0] - сам объект команды
        if len(message.entities) > 1:
            if message.entities[1].type == "text_mention":
                _type = "text_mention"
                # в теории для этого случая commands.args = '[упоминание(если у человека не стоит юзернейм)] [время]'
                user = message.entities[1].user
                user = User(id=user.id, name=user.full_name)

                # получение строки со веременем
                period_text = command.args[message.entities[1].length :]
            elif message.entities[1].type == "mention":
                _type = "mention"
                # command.args = '@user [время]'
                user = command.args.split()[0]
                user = await TelethonManager.get_user(user)
                if not user:
                    return None, BAN_FOREVER
                user = User(id=user.id, name=TelethonManager.get_full_name(user))

                # получение строки со веременем
                period_text = command.args[message.entities[1].length :]
        elif command.args.split()[0].isdigit():
            _type = "id"
            # command.args = '[user_id] [время]'
            user = await TelethonManager.get_user(command.args.split()[0])
            if not user:
                return None, BAN_FOREVER
            user = User(id=user.id, name=TelethonManager.get_full_name(user))

            # получение строки со веременем
            period_text = command.args[len(command.args.split()[0]) :]
        else:
            return None, BAN_FOREVER
        if not period_text:
            return user, BAN_FOREVER
        period = time_text_to_seconds(period_text)

    return user, period
