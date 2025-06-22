from datetime import datetime

import pytz

TIMEZONE = pytz.timezone("Europe/Moscow")


def get_local_time() -> datetime:
    """Возвращает текущее время в установленном часовом поясу"""
    return datetime.now(TIMEZONE)


def utc_to_local(utc_date: datetime) -> datetime:
    """Принимает UTC дату и возвращает дату в установленном часовом поясе"""
    return pytz.utc.localize(utc_date).astimezone(TIMEZONE)
