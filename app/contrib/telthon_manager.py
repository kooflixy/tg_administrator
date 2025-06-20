import typing
from datetime import datetime, timedelta
from logging import getLogger

from telethon import TelegramClient, hints
from telethon.types import Chat, User

from config import settings

log = getLogger(__name__)

client = TelegramClient(
    "ses", api_id=settings.TELETHON_API_ID, api_hash=settings.TELETHON_API_HASH
)

CACHE_TERM = timedelta(hours=1)


class Cache:
    _cache = dict()

    def add(self, key, value) -> None:
        try:
            self._cache[key] = dict(value=value, created_at=datetime.now())
        except:
            log.exception(
                "При попытке вставить в кеш телетона произошла ошибка key=%r value=%r",
                key,
                value,
            )

    def get(self, key):
        try:
            if not key in self._cache:
                return
            record = self._cache[key]
            if record["created_at"] + CACHE_TERM < datetime.now():
                return
            return record["value"]
        except:
            log.exception(
                "При попытке достать из кеша телетона произошла ошибка key=%r", key
            )
            return


cache = Cache()


class TelethonManager:
    @staticmethod
    async def get_entity(
        entity,
    ) -> typing.Union["hints.Entity", typing.List["hints.Entity"]]:
        log.debug(
            "Были запрошены данные о телеграм чате через telethon url: %s", entity
        )
        t_s = datetime.now()
        if not entity:
            return

        cache_record = cache.get(str(entity))
        if cache_record:
            print(datetime.now() - t_s)
            return cache_record

        await client.start(bot_token=settings.TG_BOT_API_TOKEN)

        try:
            if entity.isdigit():
                ent = await client.get_input_entity(int(entity))
                res = await client.get_entity(ent)
            else:
                res = await client.get_entity(entity)
        except ValueError:
            return

        cache.add(key=entity, value=res)

        log.debug("Были получены данные о телеграм чате через telethon url: %s", entity)
        print(datetime.now() - t_s)
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
