from logging import getLogger
from typing import Literal, Optional, Union

from pydantic import BaseModel, field_serializer, field_validator

from db.classes import ActionTypeEnum
from db.data_manager import JSONManager

CHANGEABLE_SETTINGS_PATH = "db/data/changeable_settings_data.json"

log = getLogger(__name__)


class ChangeableSettings(BaseModel):
    """Настройки, которые могут меняться пользователем в течение программы
    После каждого изменения следует сохранять изменения в CHANGEABLE_SETTINGS_PATH с помощью функции ChangeableSettings.commit()
    """

    captcha_status: bool = True
    ban_if_captcha_not_passed: bool = True
    captcha_text: str = (
        "Привет, {user}! Нажми на кнопку, чтобы подтвердить, что ты не робот."
    )
    captcha_button_text: str = "Нажми на  меня!"
    captcha_waitng: int = 60
    change_of_captcha_waiting: int = 10

    max_warn_restriction: Literal[ActionTypeEnum.MUTE, ActionTypeEnum.BAN] = (
        ActionTypeEnum.MUTE
    )
    max_warn_count: int = 3
    max_warn_mute_time: int = 10
    """Измеряется в днях"""

    remove_system_messages_waiting: int = 30

    remove_ban_notifications: int = 120

    max_count_in_page: int = 5

    close_text: str = "Чат закрыт"
    already_close_text: str = "Чат уже закрыт"
    open_text: str = "Чат снова открыт"
    already_open_text: str = "Чат уже открыт"

    distribution_check_timeout: int = 60 * 12

    linkto_chat_id: Optional[Union[str, int]] = None

    ba_chat_id: Optional[Union[str, int]] = None
    ba_channel_id: Optional[Union[str, int]] = None
    ba_post: str = """<b>🌟ID:</b> {user_id}
<b>👤Пользователь:</b> {user}
<b>📋Причина:</b> {reason}
{proof}"""
    ba_text: str = "Пользователь {user} был забанен {proof}"
    unba_text: str = "Пользователь {user} был разбанен {proof}"

    local_chat_id: Optional[int] = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    def __setattr__(self, name, value):
        """Сохранение новых настроек в CHANGEABLE_SETTINGS_PATH при каждом их изменении"""
        result = super().__setattr__(name, value)

        JSONManager.insert_json(
            CHANGEABLE_SETTINGS_PATH, self.model_dump(mode="python")
        )
        return result

    @field_validator("max_warn_restriction", mode="before")
    def validate_max_warn_restriction(v: str):
        """Переделывание max_warn_restriction из строки в ActionTypeEnum во время инициализации объекта"""
        return ActionTypeEnum._value2member_map_[v]

    @field_serializer("max_warn_restriction")
    def serialize_max_warn_restriction(
        self, max_warn_restriction: ActionTypeEnum, _info
    ):
        """Переделывание max_warn_restriction из ActionTypeEnum в строку перед model_dump и сохранением"""
        return max_warn_restriction.value


data = JSONManager.get_json(CHANGEABLE_SETTINGS_PATH)
changeable_settings = ChangeableSettings(**data)

log.info("Были получены изменяемые настройки приложения %r", changeable_settings)
