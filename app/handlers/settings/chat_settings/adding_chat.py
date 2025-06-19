from logging import getLogger

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from telethon import types

from app.contrib.for_logging import name_in_log
from app.contrib.telthon_manager import TelethonManager
from app.handlers import user_commands
from app.keyboards.settings.chat import AddChatCD
from app.utils.states import AddChatForm
from db.database import async_session_factory
from db.queries.chat_orm import ChatORMHandler

log = getLogger(__name__)

router = Router()


@router.callback_query(AddChatCD.filter())
async def add_chat(
    callback: CallbackQuery, callback_data: AddChatCD, state: FSMContext
):
    """Реакция на кнопку "Добавить чат" в списке чатов"""
    log.debug('%s нажал на кнопку "Добавить чат"', name_in_log.user(callback))

    await callback.message.answer("Введите ссылку на чат или его айди")
    await state.set_state(AddChatForm.url)

    log.info(
        "Пользователя %s попросили ввести ссылку или айди чата",
        name_in_log.user(callback),
    )


@router.message(AddChatForm.url, F.text)
async def input_chat_url(message: Message, state: FSMContext):
    """Отслеживание ссылки для добавления чата в отслеживаемые + проверки"""

    log.debug(
        "%s ввёл ссылку на чат для его добавления в отслеживаемые chat_url=%r",
        name_in_log.user(message),
        message.text,
    )
    await state.clear()  # Так как у нас нет так называемого стоп-слова, бот будет запрашивать ссылку на чат до тех пор, пока не введет её правильно. Поэтому пусть лучше каждый раз жмёт на кнопку "Добавить чат"

    # Проверка на существование чата в телеграме
    try:
        chat = await TelethonManager.get_entity(message.text)
    except:
        await message.answer("⚠Произошла ошибка")
        log.exception(
            "При попытке получить чата с chat_url=%r произошла ошибка", message.text
        )
        return

    if not chat:
        await message.answer("Добавить чат не удалось, попробуйте еще раз")
        log.info(
            "%s ввёл несуществующую ссылку на чат для его добавления в отслеживаемые chat_url=%r",
            name_in_log.user(message),
            message.text,
        )
        return

    # Проверка, на тип: является ли чатом или группой
    if not isinstance(chat, types.Channel):
        await message.answer("Это не чат")
        log.info(
            "%s ввёл ссылку на чат для его добавления в отслеживаемые, но это оказался не чат chat_url=%r",
            name_in_log.user(message),
            message.text,
        )
        return

    # Проверка, является ли чатом
    if not chat.megagroup:
        await message.answer("Это не чат, а канал")
        log.info(
            "%s ввёл ссылку на чат для его добавления в отслеживаемые, но это оказался не чат, а канал chat_url=%r",
            name_in_log.user(message),
            message.text,
        )
        return

    chat_id = int("-100" + str(chat.id))

    try:
        async with async_session_factory() as session:
            # Проверка, не ялвяется ли чат уже отслеживаемым
            if chat_id in await ChatORMHandler.get_all_id(session):
                await message.answer("Чат уже отслеживается")
                log.info(
                    "%s ввёл ссылку на чат для его добавления в отслеживаемые, но он уже отслеживается chat_url=%r",
                    name_in_log.user(message),
                    message.text,
                )
                return

            # Добавление чата в отслеживаемые
            await ChatORMHandler.insert(session, chat_id, chat.title)
            await session.commit()
    except:
        await message.answer("⚠Произошла ошибка")
        log.exception(
            "При попытке добавить чат с chat_url=%r произошла ошибка", message.text
        )
        return

    await message.answer(f'Чат "<code>{chat.title}</code>" успешно добавлен')

    await user_commands.settings_cmd(message, None)
    log.info(
        "%s добавил чат в отслеживаемые chat_url=%r",
        name_in_log.user(message),
        message.text,
    )
