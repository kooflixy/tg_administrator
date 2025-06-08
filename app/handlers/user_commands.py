from logging import getLogger
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject

from app.contrib.for_logging import name_in_log
from app.keyboards.settings_menu import settings_menu_ikb, SettingsListCD
from config import settings


log = getLogger(__name__)
router = Router()

@router.message(Command('settings'))
async def settings_cmd(message: Message, command: CommandObject):
    log.debug('%s запросил настройки бота',
                name_in_log.user(message))
    # Проверка, является ли чат личным
    if message.chat.type != 'private': return

    # Проверка, является ли пользователь главным админом
    if message.from_user.id != settings.ADMIN_ID: return

    await message.answer(f'Вот твои настроечки, {message.from_user.full_name}', reply_markup=settings_menu_ikb())
    log.info('%s получил настройки бота',
                name_in_log.user(message))

@router.callback_query(SettingsListCD.filter())
async def settings_cmd_cq(callback: CallbackQuery):
    log.debug('%s запросил настройки бота через инлайн-кнопку',
                name_in_log.user(callback))
    
    await callback.message.edit_text(f'Вот твои настроечки, {callback.from_user.full_name}', reply_markup=settings_menu_ikb())

    log.info('%s получил настройки бота, запрошенные через инлайн-кнопку',
                name_in_log.user(callback))