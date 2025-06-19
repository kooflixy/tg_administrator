import typing
from logging import getLogger

from telethon import TelegramClient, hints
from telethon.types import User

from config import settings

log = getLogger(__name__)

client = TelegramClient(
    "ses", api_id=settings.TELETHON_API_ID, api_hash=settings.TELETHON_API_HASH
)


class TelethonManager:
    @staticmethod
    async def get_entity(
        entity,
    ) -> typing.Union["hints.Entity", typing.List["hints.Entity"]]:
        log.debug(
            "Были запрошены данные о телеграм чате через telethon url: %s", entity
        )

        if not entity:
            return

        await client.start(bot_token=settings.TG_BOT_API_TOKEN)

        try:
            if entity.isdigit():
                entity = await client.get_input_entity(int(entity))
            res = await client.get_entity(entity)
        except ValueError:
            return

        log.debug("Были получены данные о телеграм чате через telethon url: %s", entity)
        return res

    @staticmethod
    async def get_user(entity) -> User:
        user = await TelethonManager.get_entity(entity)

        if not user:
            return

        # Проверка, на тип: является ли пользователем
        if not isinstance(user, User):
            return

        return user

    @staticmethod
    def get_full_name(user: User) -> str:
        names = [user.first_name, user.last_name]
        if None in names:
            names.remove(None)
        user_full_name = " ".join(names)
        return user_full_name
