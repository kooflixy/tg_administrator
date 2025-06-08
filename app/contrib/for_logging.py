from aiogram.types import Message


class UserForLogs:
    '''Класс для удобного создания записи пользователя телеграма для логов'''
    @staticmethod
    def from_msg(msg: Message) -> str:
        info_list = []
        info_list.append(f'username="{msg.from_user.full_name}"')
        info_list.append(f'user_id="{msg.from_user.id}"')
        if msg.chat.type != 'private':
            info_list.append(f'{msg.chat.type}_name={msg.chat.title}')
            info_list.append(f'{msg.chat.type}_id={msg.chat.id}')
        return f'<TgUser {', '.join(info_list)}>'