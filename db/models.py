import enum
from typing import Optional
from sqlalchemy import Enum, ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base, updated_attp

# Так как скорость работы для нас довольно важна, стараемся максимально свести всё к абстракциям

class ChatORM(Base):
    __tablename__ = 'chat_table'

    chat_id: Mapped[BigInteger]

class ModeratorORM(Base):
    __tablename__ = 'moderator_table'
    
    user_id: Mapped[BigInteger]
    updated_at: Mapped[updated_attp]
    #я думаю потом сюда стоит добавить какие именно у модера есть права(бан, мут, варн)

class ActionTypeEnum(enum.Enum):
    WARN = 'warn'
    MUTE = 'mute'
    BAN = 'ban'
    TOTAL_BAN = 'total_ban'

class UserRestrictionORM(Base):
    __tablename__ = 'user_restriction_table'
    
    user_id: Mapped[BigInteger]

    by_moderator_id: Mapped[BigInteger]
    chat_id: Optional[Mapped[BigInteger]] = mapped_column(ForeignKey("chat_table.chat_id"))
    chat: Optional[Mapped["ChatORM"]] = relationship()

    action_type = mapped_column(Enum(ActionTypeEnum).values_callable)
