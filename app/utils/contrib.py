import re

def time_text_to_seconds(text):
    units = {
        # секунды
        'секунда': 1, 'секунды': 1, 'секунд': 1, 'с': 1,
        # минуты
        'минута': 60, 'минуты': 60, 'минут': 60, 'мин': 60,
        # часы
        'час': 3600, 'часа': 3600, 'часов': 3600, 'ч': 3600,
        # дни
        'день': 86400, 'дня': 86400, 'дней': 86400, 'дн': 86400,
        # месяцы (условно 30 дней)
        'месяц': 2592000, 'месяца': 2592000, 'месяцев': 2592000,
    }

    # Поиск всех пар "число + единица"
    matches = re.findall(r'(\d+)\s*([а-яА-ЯёЁ]+)', text.lower())

    total_seconds = 0
    for value, unit in matches:
        seconds = units.get(unit)
        if seconds:
            total_seconds += int(value) * seconds

    return total_seconds