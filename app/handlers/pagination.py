from app.utils.pagination import FirstPageErrCD, LastPageErrCD, ShowYourPageCD
from aiogram.types import CallbackQuery
from aiogram import Router

router = Router()

@router.callback_query(FirstPageErrCD.filter())
async def fisrt_page_err_message(callback: CallbackQuery, callback_data: FirstPageErrCD):
    await callback.answer('Это первая страница :(')

@router.callback_query(LastPageErrCD.filter())
async def last_page_err_message(callback: CallbackQuery, callback_data: LastPageErrCD):
    await callback.answer('Это последняя страница :(')

@router.callback_query(ShowYourPageCD.filter())
async def last_page_err_message(callback: CallbackQuery, callback_data: ShowYourPageCD):
    await callback.answer('Это страница, на которой ты находишься')