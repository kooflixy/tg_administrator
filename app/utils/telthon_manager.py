import typing
from datetime import datetime, timedelta
from logging import getLogger

from telethon import TelegramClient, hints
from telethon.types import User

from config import settings

log = getLogger(__name__)

client = TelegramClient(
    "ses", api_id=settings.TELETHON_API_ID, api_hash=settings.TELETHON_API_HASH
)

CACHE_TERM = timedelta(hours=8)


class Cache:
    """Так как с помощью Telethon предполагается много парсинга, создан кеш, чтобы не тратить время зря:)"""

    _cache = dict()
    _last_reset = datetime.now()

    def _check_cache_relevance(func):
        """Проверяет актуальность кеша, удаляет если пришло время"""

        def wrapper(self, *args, **kwargs):

            now_ = datetime.now()

            if self._last_reset + CACHE_TERM < now_:
                self._last_reset = now_
                self._cache = dict()

            return func(self, *args, **kwargs)

        return wrapper

    def add(self, key, value) -> None:
        try:
            self._cache[key] = value
        except:
            log.exception(
                "При попытке вставить в кеш telethon произошла ошибка key=%r value=%r",
                key,
                value,
            )

    @_check_cache_relevance
    def get(self, key):
        try:
            if not key in self._cache:
                return
            return self._cache[key]
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
        if not entity:
            return

        cache_record = cache.get(str(entity))
        if cache_record:
            return cache_record

        await client.start(bot_token=settings.TG_BOT_API_TOKEN)

        try:
            if isinstance(entity, int):
                ent = await client.get_input_entity(entity)
            else:
                if entity.isdigit():
                    ent = await client.get_input_entity(int(entity))
                else:
                    ent = entity
            res = await client.get_entity(ent)
        except ValueError:
            return

        cache.add(key=str(entity), value=res)
        if str(res.id) != str(entity):
            cache.add(key=str(res.id), value=res)

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
        while None in names:
            names.remove(None)
        user_full_name = " ".join(names)
        return user_full_name
