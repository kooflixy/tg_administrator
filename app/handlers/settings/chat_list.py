from logging import getLogger
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from telethon import types

from app.contrib.telthon_manager import TelethonManager
from app.contrib.for_logging import name_in_log
from app.keyboards.settings_menu import ChatListCD
from app.keyboards.settings.chat_list import ChatDetailsCD, RemoveChatCD, AddChatCD, chat_list_ikb, chat_details_ikb, removed_chat_details_ikb
from app.handlers import user_commands
from app.utils.states import AddChatForm
from db.database import async_session_factory
from db.queries.orm import AsyncORM

log = getLogger(__name__)

router = Router()

@router.callback_query(ChatListCD.filter())
async def get_chat_list(callback: CallbackQuery, callback_data: ChatListCD):
    '''Инлайн-клавиатура списка чатов в настройках'''
    log.debug('%s запросил %s страницу списка чатов', 
                name_in_log.user(callback), callback_data.page)

    # Проверка на нулевую страницу
    if not callback_data.page:
        await callback.answer('Это первая страница :(')
        log.info('%s запросил нулевую страницу', 
                    name_in_log.user(callback))
        return

    # Получение списка страниц на странице
    async with async_session_factory() as session:
        chat_list = await AsyncORM.get_chat_list_page(session, callback_data.page)
    
    # Проверка на последнюю страницу, если страница не первая
    if callback_data.page != 1:
        if not chat_list: 
            await callback.answer('Это последняя страница :(')
            log.info('%s запросил следующую страницу списка чатов, находясь на последней', 
                        name_in_log.user(callback))
            return
    
    await callback.message.edit_text('Список отслеживаемых чатов:', reply_markup=chat_list_ikb(chat_list, callback_data.page))
    log.info('%s получил %s страницу списка чатов', 
                name_in_log.user(callback), callback_data.page)


@router.callback_query(AddChatCD.filter())
async def add_chat(callback: CallbackQuery, callback_data: AddChatCD, state: FSMContext):
    '''Реакция на кнопку "Добавить чат" в списке чатов'''
    log.debug('%s нажал на кнопку "Добавить чат"', 
                name_in_log.user(callback))

    await callback.message.answer('Введите ссылку на чат или его айди')
    await state.set_state(AddChatForm.url)

    log.info('Пользователя %s попросили ввести ссылку или айди чата', 
                name_in_log.user(callback))
    

@router.message(AddChatForm.url, F.text)
async def input_chat_url(message: Message, state: FSMContext):
    '''Отслеживание ссылки для добавления чата в отслеживаемые + проверки'''

    log.debug('%s ввёл ссылку на чат для его добавления в отслеживаемые chat_url: %s', 
                name_in_log.user(message), message.text)
    await state.clear() # Так как у нас нет так называемого стоп-слова, бот будет запрашивать ссылку на чат до тех пор, пока не введет её правильно. Поэтому пусть лучше каждый раз жмёт на кнопку "Добавить чат"
    
    # Проверка на существование чата в телеграме
    try:
        chat = await TelethonManager.get_entity(message.text)
    except:
        await message.answer('Добавить чат не удалось, попробуйте еще раз')
        log.info('%s ввёл несуществующую ссылку на чат для его добавления в отслеживаемые chat_url: %s', 
                    name_in_log.user(message), message.text)
        return
    
    # Проверка, на тип: является ли чатом или группой
    if not isinstance(chat, types.Channel):
        await message.answer('Это не чат')
        log.info('%s ввёл ссылку на чат для его добавления в отслеживаемые, но это оказался не чат chat_url: %s', 
                    name_in_log.user(message), message.text)
        return
    
    # Проверка, является ли чатом
    if not chat.megagroup:
        await message.answer('Это не чат, а канал')
        log.info('%s ввёл ссылку на чат для его добавления в отслеживаемые, но это оказался не чат, а канал chat_url: %s', 
                    name_in_log.user(message), message.text)
        return

    async with async_session_factory() as session:
        # Проверка, не ялвяется ли чат уже отслеживаемым
        if chat.id in await AsyncORM.get_chat_id_list(session):
            await message.answer('Чат уже отслеживается')
            log.info('%s ввёл ссылку на чат для его добавления в отслеживаемые, но он уже отслеживается chat_url: %s', 
                        name_in_log.user(message), message.text)
            return

        # Добавление чата в отслеживаемые
        await AsyncORM.insert_chat(session, chat.id, chat.title)
        await session.commit()
    
    await message.answer(f'Чат <code>{chat.title}</code> успешно добавлен')
    log.info('%s добавил чат в отслеживаемые chat_url: %s', 
                name_in_log.user(message), message.text)

    await user_commands.settings_cmd(message, None)


@router.callback_query(ChatDetailsCD.filter())
async def get_chat_details(callback: CallbackQuery, callback_data: ChatDetailsCD):
    '''Детали чата, выбранного в списке чатов'''

    log.debug('%s запросил детали отслеживаемого чата chat_id: %s', 
                name_in_log.user(callback), callback_data.chat_id)

    # Получение чата
    async with async_session_factory() as session:
        chat = await AsyncORM.get_chat(session, callback_data.chat_id)

    # Проверка, отслеживается ли чат
    if not chat:
        await callback.answer('Этот чат не отслеживается')
        log.info('%s запросил детали отслеживаемого чата, но он не отслеживается chat_id: %s', 
                    name_in_log.user(callback), callback_data.chat_id)
        return

    await callback.message.edit_text(f'Название: <code>{chat.name}</code>\nID: <code>{chat.id}</code>', reply_markup=chat_details_ikb(chat.id, callback_data.page))
    log.info('%s получил детали отслеживаемого чата chat_id: %s', 
                name_in_log.user(callback), callback_data.chat_id)


@router.callback_query(RemoveChatCD.filter())
async def remove_chat(callback: CallbackQuery, callback_data: RemoveChatCD):
    '''Удаление чата из отслеживаемых'''
    log.debug('%s начал удаление чата из отслеживаемых chat_id: %s',
                name_in_log.user(callback), callback_data.chat_id)

    async with async_session_factory() as session:
        await AsyncORM.remove_chat(session, callback_data.chat_id)
        await session.commit()
    
    await callback.answer('Чат больше не отслеживается')
    await callback.message.edit_reply_markup(reply_markup=removed_chat_details_ikb(callback_data.page)) # Удаление инлайн-кнопки "Удалить" в деталях чата, т.к. чат уже удален
    log.info('%s удалил чат из отслеживаемых chat_id: %s',
                name_in_log.user(callback), callback_data.chat_id)