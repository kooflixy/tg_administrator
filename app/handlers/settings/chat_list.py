from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.settings_menu import ChatListCD
from app.keyboards.settings.chat_list import chat_list_ikb
from db.database import async_session_factory
from db.queries.orm import AsyncORM

router = Router()

@router.callback_query(ChatListCD.filter())
async def chats_settings(callback: CallbackQuery, callback_data = ChatListCD):
    # Проверка на нулевую страницу
    if not callback_data.page:
        await callback.answer('Это первая страница :(')
        return

    async with async_session_factory() as session:
        chat_list = await AsyncORM.get_chat_list_page(session, callback_data.page)
    
    # Проверка последнюю страницу
    if not chat_list: 
        await callback.answer('Это последняя страница :(')
        return
    
    
    await callback.message.edit_text('Список отслеживаемых чаты:', reply_markup=chat_list_ikb(chat_list, callback_data.page))
