import enum


class ActionTypeEnum(enum.Enum):
    WARN = 'WARN'
    MUTE = 'MUTE'
    BAN = 'BAN'
    TOTAL_BAN = 'TOTAL_BAN'