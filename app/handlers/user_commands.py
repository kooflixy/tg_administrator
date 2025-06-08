from logging import getLogger
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject

from app.contrib.for_logging import UserForLogs
from app.keyboards.settings_menu import settings_menu_ikb, SettingsListCD
from config import settings


logger = getLogger(__name__)
router = Router()

@router.message(Command('settings'))
async def settings_cmd(message: Message, command: CommandObject):
    # Проверка, является ли чат личным
    if message.chat.type != 'private': return

    # Проверка, является ли пользователь главным админом
    if message.from_user.id != settings.ADMIN_ID: return

    await message.answer(f'Вот твои настроечки, {message.from_user.full_name}', reply_markup=settings_menu_ikb())

@router.callback_query(SettingsListCD.filter())
async def settings_cmd_cq(callback: CallbackQuery):
    await callback.message.edit_text(f'Вот твои настроечки, {callback.from_user.full_name}', reply_markup=settings_menu_ikb())