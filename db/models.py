import enum
from typing import Literal, Optional, Union
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.dialects.postgresql import ENUM

from db.database import Base, updated_attp


class ChatORM(Base):
    __tablename__ = 'chat_table'

    chat_id: Mapped[int] = mapped_column(BigInteger)

class ModeratorORM(Base):
    __tablename__ = 'moderator_table'
    
    user_id: Mapped[int] = mapped_column(BigInteger)
    chat_id: Mapped[int] = mapped_column(BigInteger)

    updated_at: Mapped[updated_attp]
    #я думаю потом сюда стоит добавить какие именно у модера есть права(бан, мут, варн)

class ActionTypeEnum(enum.Enum):
    WARN = 'WARN'
    MUTE = 'MUTE'
    BAN = 'BAN'
    TOTAL_BAN = 'TOTAL_BAN'

class UserRestrictionORM(Base):
    __tablename__ = 'user_restriction_table'

    user_id: Mapped[int] = mapped_column(BigInteger)

    by_moderator_id: Mapped[int] = mapped_column(BigInteger)
    chat_id: Mapped[Optional[int]] = mapped_column(BigInteger)

    action_type: Mapped[Literal['WARN', 'MUTE', 'BAN', 'TOTAL_BAN']] = mapped_column(ENUM(ActionTypeEnum, name='action_type', create_type=False))

class DistributionsORM(Base):
    __tablename__ = 'distribution_table'

    chat_id: Mapped[int] = mapped_column(BigInteger)
    interval: Mapped[int]