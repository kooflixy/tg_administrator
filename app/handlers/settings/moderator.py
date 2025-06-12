from logging import getLogger
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from telethon import types

from app.contrib.telthon_manager import TelethonManager
from app.contrib.text_markup import TextMarkup
from app.contrib.for_logging import name_in_log
from app.keyboards.settings_menu import ModeratorListCD
from app.keyboards.settings.moderator import ModeratorDetailsCD, RemoveModeratorCD, AddModeratorCD, moderator_list_ikb
from app.handlers import user_commands
from app.utils.states import AddModeratorForm
from db.database import async_session_factory
from db.queries.orm import AsyncORM

log = getLogger(__name__)

router = Router()

@router.callback_query(ModeratorListCD.filter())
async def get_moderator_list(callback: CallbackQuery, callback_data: ModeratorListCD):
    '''Инлайн-клавиатура списка модераторов в настройках'''
    log.debug('%s запросил %s страницу списка модераторов', 
                name_in_log.user(callback), callback_data.page)

    # Проверка на нулевую страницу
    if not callback_data.page:
        await callback.answer('Это первая страница :(')
        log.info('%s запросил нулевую страницу списка модераторов', 
                    name_in_log.user(callback))
        return

    # Получение списка модеров для страницы
    async with async_session_factory() as session:
        chat_list = await AsyncORM.get_moderator_list_page(session, callback_data.page)
    
    # Проверка на последнюю страницу, если страница не первая
    if callback_data.page != 1:
        if not chat_list: 
            await callback.answer('Это последняя страница :(')
            log.info('%s запросил следующую страницу списка модераторов, находясь на последней', 
                        name_in_log.user(callback))
            return
    
    await callback.message.edit_text('Список модераторов :', reply_markup=moderator_list_ikb(chat_list, callback_data.page))
    log.info('%s получил %s страницу списка модераторов', 
                name_in_log.user(callback), callback_data.page)


@router.callback_query(AddModeratorCD.filter())
async def add_chat(callback: CallbackQuery, callback_data: AddModeratorCD, state: FSMContext):
    '''Реакция на кнопку "Добавить модератора" в списке модераторов'''
    log.debug('%s нажал на кнопку "Добавить модератора"', 
                name_in_log.user(callback))

    await callback.message.answer('Введите юз пользователя или его айди')
    await state.set_state(AddModeratorForm.username)

    log.info('Пользователя %s попросили ввести юз или айди пользователя для добавления его в модераторы', 
                name_in_log.user(callback))


@router.message(AddModeratorForm.username, F.text)
async def input_moderator_username(message: Message, state: FSMContext):
    '''Отслеживание юзернейма для добавления пользователя в модераторы + проверки'''

    log.debug('%s ввёл юзернейм пользоваетля для его добавления в модераторы moderator_username: %s', 
                name_in_log.user(message), message.text)
    await state.clear() # Так как у нас нет так называемого стоп-слова, бот будет запрашивать юзернейм пользователя до тех пор, пока не введет её правильно. Поэтому пусть лучше каждый раз жмёт на кнопку "Добавить чат"
    
    # Проверка на существование чата в телеграме
    try:
        user = await TelethonManager.get_entity(message.text)
    except:
        await message.answer('Добавить модератора не удалось, попробуйте еще раз')
        log.info('%s ввёл несуществующий юзернейм пользователя для его добавления в отслеживаемые moderator_username: %s', 
                    name_in_log.user(message), message.text)
        return
    
    # Проверка, на тип: является ли пользователем
    if not isinstance(user, types.User):
        await message.answer('Это не пользователь')
        log.info('%s ввёл юзернейм пользователя для его добавления в отслеживаемые, но это оказался не пользователь moderator_username: %s', 
                    name_in_log.user(message), message.text)
        return

    names = [user.first_name, user.last_name]
    names.remove(None)
    user_full_name = ' '.join(names)

    async with async_session_factory() as session:
        # Проверка, не ялвяется ли пользователь модератором
        if user.id in await AsyncORM.get_moderator_id_list(session):
            await message.answer('Пользователь уже является модератором')
            log.info('%s ввёл юзернейм пользователя для его добавления в модераторы, но он уже является им moderator_username: %s', 
                        name_in_log.user(message), message.text)
            return

        # Добавление чата в отслеживаемые
        await AsyncORM.insert_moderator(session, user.id, user_full_name)
        await session.commit()
    
    await message.answer(f'Пользователь {TextMarkup.tag_user(user_full_name, user.id)} теперь модератор', parse_mode="Markdown")
    log.info('%s добавил пользователя в модераторы moderator_username: %s', 
                name_in_log.user(message), message.text)

    await user_commands.settings_cmd(message, None)
