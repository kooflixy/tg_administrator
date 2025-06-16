from logging import getLogger
from aiogram import Router
from aiogram.types import CallbackQuery
from app.contrib.for_logging import name_in_log
from app.contrib.text_markup import TextMarkup
from app.keyboards.settings.moderator import ChangeModeratorChatPermissionCD, ModeratorChatDetailsCD, ModeratorChatListCD, RemoveModeratorChatCD, moderator_chat_details_ikb, moderator_chat_list_ikb
from app.utils.answer_templates import error_cb_ans
from db.database import async_session_factory
from db.queries import ModeratorChatORMHandler

log = getLogger(__name__)

router = Router()


@router.callback_query(ModeratorChatListCD.filter())
async def get_moderator_chat_list(callback: CallbackQuery, callback_data: ModeratorChatListCD):
    '''Отображение списка модерируемых чатов модератора'''
    log.debug('%s запросил %s страницу списка чатов модератора moderator_id=%s', name_in_log.user(callback), callback_data.cur_page, callback_data.moderator_id)

    # Получение списка чатов для страницы
    try:
        async with async_session_factory() as session:
            chat_list = await ModeratorChatORMHandler.get_page(session, callback_data.cur_page, callback_data.moderator_id)
            is_last_page = await ModeratorChatORMHandler.is_last_page(session, callback_data.cur_page, callback_data.moderator_id)
    except:
        await error_cb_ans(callback)
        log.exception('При попытке получить страницу чатов модератора произошла ошибка page=%s moderator_id=%s', callback_data.cur_page, callback_data.moderator_id)
        return
    
    await callback.message.edit_text('📋Список модерируемых чатов:', reply_markup=moderator_chat_list_ikb(chat_list, callback_data.cur_page, callback_data.moderator_id, is_last_page))
    log.info('%s получил %s страницу списка чатов moderator_id=%s', name_in_log.user(callback), callback_data.cur_page, callback_data.moderator_id)


@router.callback_query(ModeratorChatDetailsCD.filter())
async def get_moderator_chat_details(callback: CallbackQuery, callback_data: ModeratorChatDetailsCD):
    '''Отображение деталей модерируемого чата модератора'''
    log.debug('%s запросил детали модерируемого чата moderator_id=%s chat_id=%s', name_in_log.user(callback), callback_data.moderator_id, callback_data.chat_id)

    # Получение модерируемого чата
    try:
        async with async_session_factory() as session:
            moderator_chat = await ModeratorChatORMHandler.get_by_moderator_and_chat_ids(session, callback_data.moderator_id, chat_id=callback_data.chat_id)
    except:
        await error_cb_ans(callback)
        log.exception('При попытке получить детали модерируемого модератором чата произошла ошибка moderator_id=%s chat_id=%s', callback_data.moderator_id, callback_data.chat_id)
        return


    if not moderator_chat:
        await callback.answer('Этот чат не модерируется этим модератором')
        log.info('%s запросил детали чата, не модерируемого выбранным модератором, moderator_id=%s chat_id=%s', name_in_log.user(callback), callback_data.moderator_id, callback_data.chat_id)
        return

    await callback.message.edit_text(
        text=
f'''
Модератор: {TextMarkup.tag_user(moderator_chat.moderator.name, moderator_chat.moderator.id)}
Чат: "{moderator_chat.chat.name}"
Имеет такие возможности:
''',
        reply_markup=moderator_chat_details_ikb(back_page=callback_data.back_page, moderator=moderator_chat),
    )
    log.info('%s получил детали модерируемого чата moderator_id=%s chat_id=%s', name_in_log.user(callback), callback_data.moderator_id, callback_data.chat_id)



@router.callback_query(ChangeModeratorChatPermissionCD.filter())
async def change_moderator_chat_permission(callback: CallbackQuery, callback_data: ChangeModeratorChatPermissionCD):
    '''Изменение какого-либо права модератора в модерируемом чате'''
    log.debug('%s пытается изменить право модератора в чате moderator_id=%s chat_id=%s perm_name=%r', name_in_log.user(callback), callback_data.moderator_id, callback_data.chat_id, callback_data.perm_name)

    # Изменение права и получение новой записи
    try:
        async with async_session_factory() as session:
            await ModeratorChatORMHandler.change_permission(session, moderator_id=callback_data.moderator_id, chat_id=callback_data.chat_id, perm_name=callback_data.perm_name)
            
            await session.commit()
            
            moderator_chat = await ModeratorChatORMHandler.get_by_moderator_and_chat_ids(session, moderator_id=callback_data.moderator_id, chat_id=callback_data.chat_id)
    except:
        await error_cb_ans(callback)
        log.exception('При попытке изменить право модератора в чате произошла ошибка moderator_id=%s chat_id=%s perm_name=%r', callback_data.moderator_id, callback_data.chat_id, callback_data.perm_name)
        return
    
    if not moderator_chat:
        await callback.answer('Этот чат не модерируется этим модератором')
        log.info('%s запросил попытался изменить права модератора в чате, не модерируемом им, moderator_id=%s chat_id=%s', name_in_log.user(callback), callback_data.moderator_id, callback_data.chat_id)
        return
    
    await callback.message.edit_reply_markup(reply_markup=moderator_chat_details_ikb(back_page=callback_data.back_page, moderator=moderator_chat))
    log.info('%s изменил право модератора в чате moderator_id=%s chat_id=%s perm_name=%r', name_in_log.user(callback), callback_data.moderator_id, callback_data.chat_id, callback_data.perm_name)

@router.callback_query(RemoveModeratorChatCD.filter())
async def remove_moderator(callback: CallbackQuery, callback_data: RemoveModeratorChatCD):
    log.debug('%s пытается удалить модерируемый чат модератора moderator_id=%s chat_id=%s', name_in_log.user(callback), callback_data.moderator_id, callback_data.chat_id)
    try:
        async with async_session_factory() as session:
            await ModeratorChatORMHandler.remove_by_moderator_and_chat_ids(session, moderator_id=callback_data.moderator_id, chat_id=callback_data.chat_id)
            await session.commit()
    except:
        await error_cb_ans(callback)
        log.exception('При попытке удалить чат из модерируемых модератора произошла ошибка moderator_id=%s chat_id=%s', callback_data.moderator_id, callback_data.chat_id)
        return


    await callback.answer('Модератор больше не заведует чатом')

    await get_moderator_chat_list(callback, ModeratorChatListCD(cur_page=callback_data.back_page, moderator_id=callback_data.moderator_id))
    log.info('%s удалил чат из модерируемых модератора moderator_id=%s chat_id=%s', name_in_log.user(callback), callback_data.moderator_id, callback_data.chat_id)

