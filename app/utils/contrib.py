import asyncio
import re
from dataclasses import dataclass
from datetime import timedelta
from logging import getLogger
from typing import Optional

from aiogram.filters import CommandObject
from aiogram.types import ChatPermissions, Message

from app.bot_obj import bot
from app.utils.telthon_manager import TelethonManager

MUTE_FOREVER = "FOREVER"

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

    def __repr__(self):
        return f"TgUser(id={self.id}, name={self.name!r})"


async def get_user_id_name(message: Message, command: CommandObject) -> Optional[User]:
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name

        user = User(id=user_id, name=user_name)
    else:
        if not command.args:
            return

        # message.entities[0] - сам объект команды
        if len(message.entities) >= 2:
            if message.entities[1].type == "text_mention":
                # в теории для этого случая commands.args = '[упоминание(если у человека не стоит юзернейм)] [время]'
                user = message.entities[1].user
                user = User(id=user.id, name=user.full_name)

            elif message.entities[1].type == "mention":
                # command.args = '@user [время]'
                user = command.args.split()[0]
                user = await TelethonManager.get_user(user)
                if not user:
                    return
                user = User(id=user.id, name=TelethonManager.get_full_name(user))
            elif command.args.split()[0].isdigit():
                # command.args = '[user_id] [время]'
                user = await TelethonManager.get_user(command.args.split()[0])
                if not user:
                    return
                user = User(id=user.id, name=TelethonManager.get_full_name(user))
            else:
                return
        else:
            return

    return user


async def get_user_id_name_period(
    message: Message, command: CommandObject
) -> tuple[Optional[User], Optional[timedelta]]:
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name

        user = User(id=user_id, name=user_name)

        if not command.args:
            return user, MUTE_FOREVER

        period = timedelta(seconds=time_text_to_seconds(command.args))

    else:
        if not command.args:
            return None, None

        # message.entities[0] - сам объект команды
        if len(message.entities) >= 2:
            if message.entities[1].type == "text_mention":
                # в теории для этого случая commands.args = '[упоминание(если у человека не стоит юзернейм)] [время]'
                user = message.entities[1].user
                user = User(id=user.id, name=user.full_name)

                # получение строки со веременем
                period_text = command.args[message.entities[1].length :]
            elif message.entities[1].type == "mention":
                # command.args = '@user [время]'
                user = command.args.split()[0]
                user = await TelethonManager.get_user(user)
                if not user:
                    return None, MUTE_FOREVER
                user = User(id=user.id, name=TelethonManager.get_full_name(user))

                # получение строки со веременем
                period_text = command.args[message.entities[1].length :]
            elif command.args.split()[0].isdigit():
                # command.args = '[user_id] [время]'
                user = await TelethonManager.get_user(command.args.split()[0])
                if not user:
                    return None, MUTE_FOREVER
                user = User(id=user.id, name=TelethonManager.get_full_name(user))

                # получение строки со веременем
                period_text = command.args[len(command.args.split()[0]) :]
            else:
                return None, MUTE_FOREVER
        else:
            return None, MUTE_FOREVER
        if not period_text:
            return user, MUTE_FOREVER
        if not period_text.isdigit():
            return user, None
        period = timedelta(seconds=time_text_to_seconds(period_text))

    return user, period


async def get_user_id_name_reason(
    message: Message, command: CommandObject
) -> tuple[Optional[User], Optional[str]]:
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.full_name

        user = User(id=user_id, name=user_name)

        if not command.args:
            return user, None

        reason = command.args

    else:
        if not command.args:
            return None, None

        # message.entities[0] - сам объект команды
        if len(message.entities) >= 2:
            if message.entities[1].type == "text_mention":
                # в теории для этого случая commands.args = '[упоминание(если у человека не стоит юзернейм)] [причина]'
                user = message.entities[1].user
                user = User(id=user.id, name=user.full_name)

                # получение причины варна
                reason = command.args[message.entities[1].length :]
            elif message.entities[1].type == "mention":
                # command.args = '@user [причина]'
                user = command.args.split()[0]
                user = await TelethonManager.get_user(user)
                if not user:
                    return None, None
                user = User(id=user.id, name=TelethonManager.get_full_name(user))

                # получение причины варна
                reason = command.args[message.entities[1].length :]
            elif command.args.split()[0].isdigit():
                # command.args = '[user_id] [причина]'
                user = await TelethonManager.get_user(command.args.split()[0])
                if not user:
                    return None, None
                user = User(id=user.id, name=TelethonManager.get_full_name(user))

                # получение причины варна
                reason = command.args[len(command.args.split()[0]) :]
            else:
                return None, None
        else:
            return None, None

    reason = reason.strip()

    return user, reason


def get_msg_url_reason(
    message: Message, command: CommandObject
) -> tuple[Optional[str], Optional[str]]:
    if message.reply_to_message:
        msg_url = message.reply_to_message.get_url()

        reason = command.args if command.args else ""
    else:
        if len(message.entities) < 2:
            return None, None

        url_ent = message.entities[1]
        if url_ent.type == "url":
            msg_url = message.text[url_ent.offset : url_ent.offset + url_ent.length]
        else:
            return None, None
        reason = message.text[url_ent.offset + url_ent.length :].strip()

    return msg_url, reason
