from logging import getLogger

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from telethon import types

from app.contrib.for_logging import name_in_log
from app.contrib.telthon_manager import TelethonManager
from app.contrib.text_markup import TextMarkup
from app.handlers import user_commands
from app.keyboards.settings.moderator import AddModeratorCD
from app.utils.states import AddModeratorForm
from db.database import async_session_factory
from db.queries.moderator_orm import ModeratorORMHandler

log = getLogger(__name__)

router = Router()


@router.callback_query(AddModeratorCD.filter())
async def add_moderator(
    callback: CallbackQuery, callback_data: AddModeratorCD, state: FSMContext
):
    """Реакция на кнопку "Добавить модератора" в списке модераторов"""
    log.debug('%s нажал на кнопку "Добавить модератора"', name_in_log.user(callback))

    await callback.message.answer("Введите юз пользователя или его айди")
    await state.set_state(AddModeratorForm.username)

    log.info(
        "Пользователя %s попросили ввести юз или айди пользователя для добавления его в модераторы",
        name_in_log.user(callback),
    )


@router.message(AddModeratorForm.username, F.text)
async def input_moderator_username(message: Message, state: FSMContext):
    """Отслеживание юзернейма для добавления пользователя в модераторы + проверки"""

    log.debug(
        "%s ввёл юзернейм пользоваетля для его добавления в модераторы moderator_username=%r",
        name_in_log.user(message),
        message.text,
    )
    await state.clear()  # Так как у нас нет так называемого стоп-слова, бот будет запрашивать юзернейм пользователя до тех пор, пока не введет её правильно. Поэтому пусть лучше каждый раз жмёт на кнопку "Добавить чат"

    # Проверка на существование чата в телеграме
    try:
        user = await TelethonManager.get_entity(message.text)
    except:
        await message.answer("⚠Произошла ошибка")
        log.exception(
            "При попытке получить пользователя с username=%r произошла ошибка",
            message.text,
        )
        return

    if not user:
        await message.answer("Добавить модератора не удалось, попробуйте еще раз")
        log.info(
            "%s ввёл несуществующий юзернейм пользователя для его добавления в отслеживаемые moderator_username=%r",
            name_in_log.user(message),
            message.text,
        )
        return

    # Проверка, на тип: является ли пользователем
    if not isinstance(user, types.User):
        await message.answer("Это не пользователь")
        log.info(
            "%s ввёл юзернейм пользователя для его добавления в отслеживаемые, но это оказался не пользователь moderator_username=%r type=%r",
            name_in_log.user(message),
            message.text,
            type(user),
        )
        return

    user_full_name = TelethonManager.get_full_name(user)

    try:
        async with async_session_factory() as session:
            # Проверка, не ялвяется ли пользователь модератором
            if user.id in await ModeratorORMHandler.get_all_id(session):
                await message.answer("Пользователь уже является модератором")
                log.info(
                    "%s ввёл юзернейм пользователя для его добавления в модераторы, но он уже является им moderator_username=%r moderator_id=%s",
                    name_in_log.user(message),
                    message.text,
                    user.id,
                )
                return

            # Добавление чата в отслеживаемые
            await ModeratorORMHandler.insert(session, user.id, user_full_name)
            await session.commit()
    except:
        await message.answer("⚠Произошла ошибка")
        log.exception(
            "При попытке добавить модератора произошла ошибка moderator_username=%r moderator_id=%s",
            message.text,
            user.id,
        )

    await message.answer(
        f"Пользователь {TextMarkup.tag_user(user_full_name, user.id)} теперь модератор✅"
    )
    log.info(
        "%s добавил пользователя в модераторы moderator_username=%s moderator_id=%s",
        name_in_log.user(message),
        message.text,
        user.id,
    )

    await user_commands.settings_cmd(message, None)
