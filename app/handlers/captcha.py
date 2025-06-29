import asyncio
from logging import getLogger

from aiogram import Router
from aiogram.types import CallbackQuery, ChatMemberUpdated

from app.bot_obj import bot
from app.keyboards.captcha_btn import CaptchaPassedCD, captcha_btn_ikb
from app.utils.for_logging import name_in_log
from app.utils.rest_handler.ban_rest import BanRestHandler
from app.utils.text_markup import TextMarkup
from config import changeable_settings
from db.database import async_session_factory

SLEEP_TIME = 2  # в секундах
DELETE_MSG_TIME = 1

log = getLogger(__name__)

router = Router()


class NotPassedCaptchaUsers:
    user_list = []

    def append(self, user_id: int):
        if user_id not in self.user_list:
            self.user_list.append(user_id)

    def remove(self, user_id: int):
        if user_id in self.user_list:
            self.user_list.remove(user_id)

    def is_captha_passed(self, user_id: int):
        return user_id not in self.user_list


not_passed_captcha_users = NotPassedCaptchaUsers()


async def captcha_check(event: ChatMemberUpdated):
    """Функция, отвечающая за капчу
    При её вызове пользователю отправляется приветствие с просьбой пройти капчу в виде кнопки
    1) Пользователь добавляется в список еще не прошедших капчу - not_passed_captcha_users
    2) В этой же функции стартует асинхронный sleep на выбранное время
    3) При нажатии на кнопку капчи пользователь удаляется из списка not_passed_captcha_users с помощью функции pass_captcha(), описанной ниже
    4) sleep оканчивается
    5) С помощью not_passed_captcha_users проверяется, прошел ли пользователь капчу"""
    new_member = event.new_chat_member.user
    if new_member.is_bot:
        return

    not_passed_captcha_users.append(new_member.id)

    # Отвечаем пользователю, сразу же добавляя кнопку капчи
    captcha_msg = await event.answer(
        text=TextMarkup.get_captcha_text(
            user_full_name=new_member.full_name, user_id=new_member.id
        ),
    )
    await captcha_msg.edit_reply_markup(
        reply_markup=captcha_btn_ikb(new_member.id, captcha_msg.message_id)
    )
    log.debug("%s было предложено пройти капчу", name_in_log.user(event))

    # Ждём отведенный срок. Сделано через for, потому что если пользователь прошел, вышел и зашел снова, то если он зайдет до истечения этого sleep, его удалят с прошлой првоерки
    for _ in range(changeable_settings.captcha_waitng // SLEEP_TIME):
        await asyncio.sleep(SLEEP_TIME)
        if not_passed_captcha_users.is_captha_passed(new_member.id):
            return

    # Проверка, успел ли пользователь нажать на кнопку капчи. Если нет, то кикаем
    if not not_passed_captcha_users.is_captha_passed(new_member.id):
        tag_user_text = TextMarkup.tag_user(
            user_full_name=new_member.full_name, user_id=new_member.id
        )

        # Кик пользователя. В aiogram нет отдельной функции кика, поэтому мы сначала удаляем пользоватея с помощью бана, а затем разбаниваем его
        await bot.ban_chat_member(event.chat.id, new_member.id)
        if not changeable_settings.ban_if_captcha_not_passed:
            # если мы всё-таки хотим забанить пользователя :(
            await bot.unban_chat_member(event.chat.id, new_member.id)
        else:
            async with async_session_factory() as session:
                await BanRestHandler.apply_restriction(
                    session,
                    moderator_id=bot.id,
                    chat_id=event.chat.id,
                    user_id=event.from_user.id,
                )
                await session.commit()

        rest_str = (
            "забанен" if changeable_settings.ban_if_captcha_not_passed else "кикнут"
        )

        captcha_not_passed_message = await event.answer(
            f"{tag_user_text} не прошел капчу, за что был {rest_str}"
        )
        await bot.delete_message(
            chat_id=event.chat.id, message_id=captcha_msg.message_id
        )  # Удаляем сообщение с капчой

        await asyncio.sleep(DELETE_MSG_TIME)
        await bot.delete_message(
            chat_id=event.chat.id, message_id=captcha_not_passed_message.message_id
        )  # Удаляем сообщение о непрохождении капчи

        not_passed_captcha_users.remove(new_member.id)
        log.info("%s не прошел капчу", name_in_log.user(event))


@router.callback_query(CaptchaPassedCD.filter())
async def pass_captcha(callback: CallbackQuery, callback_data: CaptchaPassedCD):
    """Удаляет пользователя из not_passed_captcha_users, из чего после следует, что он прошел капчу"""
    if callback.from_user.id != callback_data.user_id:
        await callback.answer("Не твоё не трогай")
        return

    tag_user_text = TextMarkup.tag_user(
        callback.from_user.full_name, callback.from_user.id
    )

    not_passed_captcha_users.remove(callback_data.user_id)
    welcome_message = await callback.message.answer(
        f"{tag_user_text}, добро пожаловать!"
    )
    await bot.delete_message(
        chat_id=callback.message.chat.id, message_id=callback_data.captcha_msg_id
    )  # Удаляем сообщение с капчой

    await asyncio.sleep(DELETE_MSG_TIME)

    await bot.delete_message(
        chat_id=welcome_message.chat.id, message_id=welcome_message.message_id
    )  # Удаляем сообщение с добро пожаловать!

    log.info("%s успешно прошел капчу", name_in_log.user(callback))
