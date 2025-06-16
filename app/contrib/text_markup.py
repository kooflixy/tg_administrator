from config.changeable_config import changeable_settings


class TextMarkup:
    def tag_user(user_full_name: str, user_id: int) -> str:
        res = f'<a href="tg://user?id={user_id}">{user_full_name}</a>'
        return res
    
    def get_captcha_text(user_full_name: str, user_id: int):
        if '{user}' in changeable_settings.captcha_text:
            return changeable_settings.captcha_text.format(
                user=TextMarkup.tag_user(user_full_name, user_id)
            )
        return changeable_settings.captcha_text