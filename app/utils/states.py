from aiogram.fsm.state import State, StatesGroup


class AddChatForm(StatesGroup):
    url = State()


class AddModeratorForm(StatesGroup):
    username = State()


class ChangeCaptchaTextForm(StatesGroup):
    type = State()
    new_text = State()
