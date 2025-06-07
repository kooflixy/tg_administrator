import typing
from telethon import TelegramClient, hints
from config import settings

client = TelegramClient('ses', api_id=settings.TELETHON_API_ID, api_hash=settings.TELETHON_API_HASH)

class TelethonManager:
    @staticmethod
    async def get_entity(entity) -> typing.Union['hints.Entity', typing.List['hints.Entity']]:
        await client.start(bot_token=settings.TG_BOT_API_TOKEN)
        return await client.get_entity(entity)