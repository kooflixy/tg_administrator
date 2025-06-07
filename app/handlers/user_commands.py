from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject

from app.keyboards.settings_menu import settings_menu_ikb, SettingsListCD
from config import settings


router = Router()

@router.message(Command('settings'))
async def settings_cmd(message: Message, command: CommandObject):
    if message.from_user.id != settings.ADMIN_ID: return

    await message.answer(f'Вот твои настроечки, {message.from_user.full_name}', reply_markup=settings_menu_ikb())

@router.callback_query(SettingsListCD.filter())
async def settings_cmd_cq(callback: CallbackQuery):
    if callback.from_user.id != settings.ADMIN_ID: return

    await callback.message.edit_text(f'Вот твои настроечки, {callback.from_user.full_name}', reply_markup=settings_menu_ikb())