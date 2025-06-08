import enum


class ActionTypeEnum(enum.Enum):
    '''Значения для наказаний, используемые в бд'''
    WARN = 'WARN'
    MUTE = 'MUTE'
    BAN = 'BAN'
    TOTAL_BAN = 'TOTAL_BAN'