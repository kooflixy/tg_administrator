from dataclasses import dataclass
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


@dataclass
class ModerIdArg:
    moderator_id: int


@dataclass
class UserIdArg:
    user_id: Optional[int]


@dataclass
class PermNameArg:
    perm: str


@dataclass
class DistIdArg:
    dist_id: int


@dataclass
class DistMsgIdArg:
    msg_id: int


@dataclass
class CurrentPageArg:
    cur_page: int = 1


@dataclass
class BackPageArg:
    back_page: int = 1


@dataclass
class ChatIDArg:
    chat_id: int


@dataclass
class ModerChatIdCDArg(ChatIDArg): ...


def back_ibtn(callback_data) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙Назад", callback_data=callback_data.pack())
    return builder
