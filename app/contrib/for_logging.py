from typing import overload
from aiogram.types import Message, CallbackQuery

class name_in_log:
    '''Класс для удобного создания имён для логов'''

    # Для пользователя
    @staticmethod
    @overload
    def user(msg: Message) -> str: ...
    
    @staticmethod
    @overload
    def user(callback: CallbackQuery) -> str: ...

    @staticmethod
    def user(entity) -> str:
        if isinstance(entity, Message): return f'TgUser(id={entity.from_user.id})'
        return f'TgUser(id={entity.message.from_user.id})'