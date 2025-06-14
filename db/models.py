import enum
from typing import Annotated, Literal, Optional
from sqlalchemy import BigInteger, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM

from db.database import Base, updated_attp
from db.classes import ActionTypeEnum

permission_tp = Annotated[bool, mapped_column(default=False)]

class Adm:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str]

class ChatORM(Adm, Base):
    __tablename__ = 'chat_table'

    moderators: Mapped[list["LnkChatModeratorORM"]] = relationship(lazy='joined')

class ModeratorORM(Adm, Base):
    __tablename__ = 'moderator_table'

    chats: Mapped[list["LnkChatModeratorORM"]] = relationship(lazy='joined')

class LnkChatModeratorORM(Base):
    __tablename__ = 'lnk_chat_moderator_table'

    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('chat_table.id'))
    chat: Mapped["ChatORM"] = relationship(back_populates='moderators')
    moderator_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('moderator_table.id'))
    moderator: Mapped["ModeratorORM"] = relationship(back_populates='chats')

    # Права
    ba_perm: Mapped[permission_tp]
    ban_perm: Mapped[permission_tp]
    kick_perm: Mapped[permission_tp]
    mute_perm: Mapped[permission_tp]
    warn_perm: Mapped[permission_tp]

    updated_at: Mapped[updated_attp]

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