from config.changeable_config import changeable_settings


class TextMarkup:
    def tag_user(user_full_name: str, user_id: int) -> str:
        res = f'<a href="tg://user?id={user_id}">{user_full_name}</a>'
        return res

    def get_captcha_text(user_full_name: str, user_id: int):
        if "{user}" in changeable_settings.captcha_text:
            return changeable_settings.captcha_text.format(
                user=TextMarkup.tag_user(user_full_name, user_id)
            )
        return changeable_settings.captcha_text

    def get_ba_post(user_id: int, user_full_name: str, reason: str, proof: str):
        return changeable_settings.ba_post.format(
            user_id=f"<code>{user_id}</code>", user=TextMarkup.tag_user(user_full_name, user_id), reason=reason, proof=f'<a href="{proof}">доказательства</a>'
        )
    
    def get_ba_text(user_id: int, user_full_name: str, proof: str):
        return changeable_settings.ba_text.format(
            user_id=f"<code>{user_id}</code>", user=TextMarkup.tag_user(user_full_name, user_id), proof=proof
        )
    
    def get_unba_text(user_id: int, user_full_name: str, proof: str):
        return changeable_settings.unba_text.format(
            user_id=f"<code>{user_id}</code>", user=TextMarkup.tag_user(user_full_name, user_id), proof=proof
        )