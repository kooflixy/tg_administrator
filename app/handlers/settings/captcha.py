from logging import getLogger
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.handlers.user_commands import settings_cmd
from app.keyboards.settings_menu import SettingsType, SettingsTypeCD
from app.keyboards.settings.captcha import *
from app.utils.states import ChangeCaptchaTextForm
from config import changeable_settings


log = getLogger(__name__)

router = Router()

@router.callback_query(SettingsTypeCD.filter(F.type==SettingsType.CAPTCHA))
async def captcha_settings(callback: CallbackQuery, callback_data: SettingsTypeCD):
    await callback.message.edit_text(
    text=
f'''<b>Статус</b>: {'Включено✅' if changeable_settings.captcha_status else 'Выключено❌'}
<b>🕐Время:</b> {changeable_settings.captcha_waitng} сек.
<b>📜Текст сообщения:</b> {changeable_settings.captcha_text}
<b>🔔Текст кнопки капчи:</b> {changeable_settings.captcha_button_text}''',
    reply_markup=captcha_settings_ikb()
    )

@router.callback_query(ChangeCaptchaStatusCD.filter())
async def change_captcha_status(callback: CallbackQuery, callback_data: ChangeCaptchaStatusCD):
    changeable_settings.captcha_status =  not changeable_settings.captcha_status
    await captcha_settings(callback, None)

@router.callback_query(ChangeCaptchaWaitingTimeCD.filter())
async def change_captcha_waiting_time(callback: CallbackQuery, callback_data: ChangeCaptchaWaitingTimeCD):
    if callback_data.action == ChangeCaptchaWaitingTimeActions.DOWN:
        if changeable_settings.captcha_waitng - changeable_settings.change_of_captcha_waiting < 0:
            await callback.answer('Время не может быть отрицательным(')
            return
        changeable_settings.captcha_waitng -= changeable_settings.change_of_captcha_waiting
    else:
        changeable_settings.captcha_waitng += changeable_settings.change_of_captcha_waiting
        
    await captcha_settings(callback, None)

@router.callback_query(ChangeCaptchaTextCD.filter())
async def change_captcha_text(callback: CallbackQuery, callback_data: ChangeCaptchaTextCD, state: FSMContext):
    await state.update_data(type=callback_data.type)
    await state.set_state(ChangeCaptchaTextForm.new_text)

    if callback_data.type == ChangeCaptchaTextTypes.MESSAGE:
        await callback.message.answer(f'Введите новый текст сообщения' + '\n*{user} - имя пользователя с ссылкой на него')
    elif callback_data.type == ChangeCaptchaTextTypes.BUTTON:
        await callback.message.answer(f'Введите новый текст кнопки')
    

@router.message(ChangeCaptchaTextForm.new_text, F.text)
async def set_captcha_text(message: Message, state: FSMContext):
    await state.update_data(new_text=message.text)
    data = await state.get_data()
    await state.clear()

    
    if data['type'] == ChangeCaptchaTextTypes.MESSAGE:
        changeable_settings.captcha_text = message.text
    elif data['type'] == ChangeCaptchaTextTypes.BUTTON:
        changeable_settings.captcha_button_text = message.text

    await message.answer('Успешно изменено!')

    await settings_cmd(message, None)