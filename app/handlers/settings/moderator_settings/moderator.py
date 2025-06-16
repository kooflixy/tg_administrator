from logging import getLogger
from aiogram import F, Router
from aiogram.types import CallbackQuery
from app.contrib.for_logging import name_in_log
from app.contrib.text_markup import TextMarkup
from app.keyboards.settings_menu import ModeratorListCD
from app.keyboards.settings.moderator import RemoveModeratorCD, moderator_details_ikb, moderator_list_ikb, ModeratorDetailsCD
from app.utils.answer_templates import error_cb_ans
from db.database import async_session_factory
from db.queries import ModeratorORMHandler

log = getLogger(__name__)

router = Router()


@router.callback_query(ModeratorListCD.filter())
async def get_moderator_list(callback: CallbackQuery, callback_data: ModeratorListCD):
    '''Инлайн-клавиатура списка модераторов в настройках'''
    log.debug('%s запросил %s страницу списка модераторов', name_in_log.user(callback), callback_data.cur_page)
    
    # Получение списка модеров
    try:
        async with async_session_factory() as session:
            moderator_list = await ModeratorORMHandler.get_page(session, callback_data.cur_page)
            is_last_page = await ModeratorORMHandler.is_last_page(session, callback_data.cur_page)
    except:
        await error_cb_ans(callback)
        log.exception('При попытке получить страницу модераторов произошла ошибка page=%s', callback_data.cur_page)
        return
    
    await callback.message.edit_text('📋Список модераторов :', reply_markup=moderator_list_ikb(moderator_list=moderator_list, page=callback_data.cur_page, is_last_page=is_last_page))
    log.info('%s получил страницу списка модераторов page=%s', name_in_log.user(callback), callback_data.cur_page)


@router.callback_query(ModeratorDetailsCD.filter())
async def get_moderator_details(callback: CallbackQuery, callback_data: ModeratorDetailsCD):
    log.debug('%s запросил детали модератора moderator_id=%s', name_in_log.user(callback), callback_data.moderator_id)

    try:
        async with async_session_factory() as session:
            moderator = await ModeratorORMHandler.get(session, callback_data.moderator_id)
    except:
        await error_cb_ans(callback)
        log.exception('При попытке получить детали модератора произошла ошибка moderator_id=%s', callback_data.moderator_id)
        return
    
    if not moderator:
        await callback.answer('Такого модератора нет')
        log.info('%s запросил детали несуществующего модератора moderator_id=%s', name_in_log.user(callback), callback_data.moderator_id)
        return

    await callback.message.edit_text(
        text=
f'''Имя: {TextMarkup.tag_user(moderator.name, moderator.id)}
ID: {moderator.id}
''',
        reply_markup=moderator_details_ikb(moderator_id=callback_data.moderator_id, back_page=callback_data.back_page)
    )
    log.info('%s получил детали модератора %r', name_in_log.user(callback), moderator)

@router.callback_query(RemoveModeratorCD.filter())
async def remove_moderator(callback: CallbackQuery, callback_data: RemoveModeratorCD):
    try:
        async with async_session_factory() as session:
            await ModeratorORMHandler.remove(session, pk_value=callback_data.moderator_id)
            await session.commit()
    except:
        await error_cb_ans(callback)
        log.exception('При попытке полностью разжаловать модератора произошла ошибка moderator_id=%s', callback_data.moderator_id)
        return

    await callback.answer('Модератор разжалован')
    log.info('%s полностью разжаловал модератора moderator_id=%r', name_in_log.user(callback), callback_data.moderator_id)

    await get_moderator_list(callback, ModeratorListCD(cur_page=callback_data.back_page))