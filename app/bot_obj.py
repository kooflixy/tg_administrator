from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from config import settings

bot = Bot(token=settings.TG_BOT_API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))