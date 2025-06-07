from telethon import TelegramClient
from config import settings

client = TelegramClient('ses', api_id=settings.TELETHON_API_ID, api_hash=settings.TELETHON_API_HASH).start(bot_token=settings.TG_BOT_API_TOKEN)
