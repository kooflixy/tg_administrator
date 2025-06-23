from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_rkb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⚙Настройки"),
        ],
        [
            KeyboardButton(text="📋Список команд"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True,
)
