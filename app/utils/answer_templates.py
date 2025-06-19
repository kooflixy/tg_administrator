from aiogram.types import CallbackQuery


async def error_cb_ans(callback: CallbackQuery):
    await callback.answer("⚠Произошла ошибка")
