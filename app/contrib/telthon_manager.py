import typing
from telethon import TelegramClient, hints
from config import settings

from logging import getLogger

log = getLogger(__name__)

client = TelegramClient('ses', api_id=settings.TELETHON_API_ID, api_hash=settings.TELETHON_API_HASH)

class TelethonManager:
    @staticmethod
    async def get_entity(entity) -> typing.Union['hints.Entity', typing.List['hints.Entity']]:
        log.debug('Были запрошены данные о телеграм чате через telethon url: %s', entity)

        await client.start(bot_token=settings.TG_BOT_API_TOKEN)
        res =  await client.get_entity(entity)

        log.debug('Были получены данные о телеграм чате через telethon url: %s', entity)
        return res