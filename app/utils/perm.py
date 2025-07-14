from typing import Union

from aiogram.types import ChatPermissions

from db.models import ChatPermORM, UserPermORM

permissions_translations = {
    "can_send_messages": "Сообщения",
    "can_send_audios": "Аудио",
    "can_send_documents": "Документы",
    "can_send_photos": "Фото",
    "can_send_videos": "Видео",
    "can_send_video_notes": "Кружки",
    "can_send_voice_notes": "Голосовые",
    "can_send_polls": "Опросы",
    "can_send_other_messages": "Др. сообщения",
    "can_add_web_page_previews": "Превью сайтов",
    "can_change_info": "Изм. чата",
    "can_invite_users": "Приглашение",
    "can_pin_messages": "Закрепление",
    "can_manage_topics": "Темы",
}


def redistribute_dict(input_dict):
    items = list(input_dict.items())
    length = len(items)
    half = (length + 1) // 2

    # Создаем два списка: первая и вторая половины
    first_half = items[:half]
    second_half = items[half:]

    # Объединяем, чередуя элементы из первой и второй половин
    result_items = []
    for i in range(max(len(first_half), len(second_half))):
        if i < len(first_half):
            result_items.append(first_half[i])
        if i < len(second_half):
            result_items.append(second_half[i])

    # Преобразуем обратно в словарь
    return dict(result_items)


def permissions_to_dict(
    current_permissions: Union[ChatPermissions, ChatPermORM, UserPermORM], **kwargs
) -> dict[str, bool]:
    def get(field: str) -> bool:
        return kwargs.get(field, getattr(current_permissions, field, False) or False)

    return dict(
        can_send_messages=get("can_send_messages"),
        can_send_audios=get("can_send_audios"),
        can_send_documents=get("can_send_documents"),
        can_send_photos=get("can_send_photos"),
        can_send_videos=get("can_send_videos"),
        can_send_video_notes=get("can_send_video_notes"),
        can_send_voice_notes=get("can_send_voice_notes"),
        can_send_polls=get("can_send_polls"),
        can_send_other_messages=get("can_send_other_messages"),
        can_add_web_page_previews=get("can_add_web_page_previews"),
        can_change_info=get("can_change_info"),
        can_invite_users=get("can_invite_users"),
        can_pin_messages=get("can_pin_messages"),
        can_manage_topics=get("can_manage_topics"),
    )


def current_to_new_permissions(
    current_permissions: ChatPermissions, **kwargs
) -> ChatPermissions:

    return ChatPermissions(**permissions_to_dict(current_permissions, **kwargs))
