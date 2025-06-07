from typing import Literal
from pydantic import BaseModel, field_serializer, field_validator

from db.data_manager import JSONManager
from db.classes import ActionTypeEnum

CHANGEABLE_SETTINGS_PATH = 'db/data/changeable_settings_data.json'


class ChangeableSettings(BaseModel):
    '''Настройки, которые могут меняться пользователем в течение программы
    После каждого изменения следует сохранять изменения в CHANGEABLE_SETTINGS_PATH с помощью функции ChangeableSettings.commit()'''
    captcha_text: str = "Привет, {user}! Нажми на кнопку, чтобы подтвердить, что ты не робот."
    captcha_waitng: int = 60

    max_warn_restriction: Literal[ActionTypeEnum.MUTE, ActionTypeEnum.BAN] = ActionTypeEnum.MUTE
    max_warn_count: int = 3

    remove_system_messages_waiting: int = 30

    remove_ban_notifications: int = 120

    max_chat_count_in_page: int = 5

    @field_validator('max_warn_restriction', mode='before')
    def validate_max_warn_restriction(v: str):
        return ActionTypeEnum._value2member_map_[v]

    @field_serializer('max_warn_restriction')
    def serialize_max_warn_restriction(self, max_warn_restriction: ActionTypeEnum, _info):
        return max_warn_restriction.value

    def commit(self):
        self.model_dump_json(indent=4)
        JSONManager.insert_json(CHANGEABLE_SETTINGS_PATH, self.model_dump(mode='python'))

data = JSONManager.get_json(CHANGEABLE_SETTINGS_PATH)
changeable_settings = ChangeableSettings(**data)