import asyncio
from logging import getLogger
from aiogram import F, Router
from aiogram.filters import IS_MEMBER, IS_NOT_MEMBER, ChatMemberUpdatedFilter
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery

from app.bot_obj import bot
from app.contrib.for_logging import name_in_log
from app.contrib.text_markup import TextMarkup
from app.keyboards.captcha_btn import captcha_btn_ikb, CaptchaPassedCD
from config import changeable_settings

log = getLogger(__name__)

router = Router()

class NotPassedCaptchaUsers:
    user_list = []

    def add(self, user_id: int):
        if user_id not in self.user_list:
            self.user_list.append(user_id)
    
    def remove(self, user_id: int):
        if user_id in self.user_list:
            self.user_list.remove(user_id)

    def is_captha_passed(self, user_id: int):
        return user_id not in self.user_list

not_passed_captcha_users = NotPassedCaptchaUsers()

async def captcha_check(event: ChatMemberUpdated):
    new_member = event.new_chat_member.user
    if new_member.is_bot: return

    not_passed_captcha_users.add(new_member.id)

    # Отвечаем пользователю, сразу же добавляя кнопку капчи
    captcha_msg = await event.answer(
        text=TextMarkup.get_captcha_text(user_full_name=new_member.full_name, user_id=new_member.id),
        parse_mode='Markdown'
    )
    await captcha_msg.edit_reply_markup(reply_markup=captcha_btn_ikb(new_member.id, captcha_msg.message_id))
    log.debug('%s было предложено пройти капчу',
                name_in_log.user(event))


    await asyncio.sleep(changeable_settings.captcha_waitng)

    if not not_passed_captcha_users.is_captha_passed(new_member.id):
        tag_user_text = TextMarkup.tag_user(user_full_name=new_member.full_name, user_id=new_member.id)

        # Кик пользователя. В aiogram нет отдельной функции кика, поэтому мы сначала удаляем пользоватея с помощью бана, а затем разбаниваем его
        await bot.ban_chat_member(event.chat.id, new_member.id)
        await bot.unban_chat_member(event.chat.id, new_member.id)

        await event.answer(f'{tag_user_text} не прошел капчу, за что был кикнут', parse_mode='Markdown')
        await bot.delete_message(chat_id=event.chat.id, message_id=captcha_msg.message_id)

        not_passed_captcha_users.remove(new_member.id)
        log.info('%s не прошел капчу',
                    name_in_log.user(event))


@router.callback_query(CaptchaPassedCD.filter())
async def pass_captcha(callback: CallbackQuery, callback_data: CaptchaPassedCD):
    if callback.from_user.id != callback_data.user_id:
        await callback.answer('Не твоё не трогай')
        return
    
    tag_user_text = TextMarkup.tag_user(callback.from_user.full_name, callback.from_user.id)

    not_passed_captcha_users.remove(callback_data.user_id)
    await callback.message.answer(f'{tag_user_text}, добро пожаловать!', parse_mode='Markdown')
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback_data.captcha_msg_id) # Удаляем сообщение с капчой

    log.info('%s успешно прошел капчу',
                name_in_log.user(callback))