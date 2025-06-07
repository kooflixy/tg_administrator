from aiogram.fsm.state import StatesGroup, State

class AddChatForm(StatesGroup):
    url = State()