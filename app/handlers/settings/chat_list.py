from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.contrib.telthon_client_obj import client
from app.keyboards.settings_menu import ChatListCD
from app.keyboards.settings.chat_list import ChatDetailsCD, RemoveChatCD, chat_list_ikb, chat_details_ikb, removed_chat_details_ikb
from db.database import async_session_factory
from db.queries.orm import AsyncORM

router = Router()

@router.callback_query(ChatListCD.filter())
async def chat_list(callback: CallbackQuery, callback_data = ChatListCD):
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
    
    await callback.message.edit_text('Список отслеживаемых чатов:', reply_markup=chat_list_ikb(chat_list, callback_data.page))

@router.callback_query(ChatDetailsCD.filter())
async def chat_details(callback: CallbackQuery, callback_data = ChatDetailsCD):
    async with async_session_factory() as session:
        chat = await AsyncORM.get_chat(session, callback_data.chat_id)

    # Проверка, отслеживается ли чат
    if not chat:
        await callback.answer('Этот чат не отслеживается')
        return

    await callback.message.edit_text(f'Название: <code>{chat.name}</code>\nID: <code>{chat.id}</code>', reply_markup=chat_details_ikb(chat.id, callback_data.page))


@router.callback_query(RemoveChatCD.filter())
async def remove_chat(callback: CallbackQuery, callback_data = RemoveChatCD):
    async with async_session_factory() as session:
        await AsyncORM.remove_chat(session, callback_data.chat_id)
        await session.commit()
    await callback.answer('Чат больше не отслеживается')
    await callback.message.edit_reply_markup(reply_markup=removed_chat_details_ikb(callback_data.page))