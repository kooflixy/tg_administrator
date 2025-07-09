import enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Annotated, List, Literal, Optional

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Interval, Table
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.classes import ActionTypeEnum
from db.database import Base, updated_attp

permission_tp = Annotated[bool, mapped_column(default=False)]


class Adm:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str]


class DistributionChatORM(Base):
    __tablename__ = "distribution_chat_table"

    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chat_table.id"))
    chat: Mapped["ChatORM"] = relationship(back_populates="distributions")
    distribution_id: Mapped[int] = mapped_column(ForeignKey("distribution_table.id"))
    distribution: Mapped["DistributionORM"] = relationship(back_populates="chats")
    last_msg_id: Mapped[Optional[int]] = mapped_column(BigInteger)


class ChatORM(Adm, Base):
    __tablename__ = "chat_table"

    moderators: Mapped[list["ModeratorChatORM"]] = relationship(lazy="joined")
    distributions: Mapped[list["DistributionChatORM"]] = relationship(
        back_populates="chat"
    )
    perms: Mapped["ChatPermORM"] = relationship()


class DistributionORM(Base):
    __tablename__ = "distribution_table"

    name: Mapped[str]
    msg_id: Mapped[int] = mapped_column(BigInteger)
    interval: Mapped[timedelta]
    next_dist_date: Mapped[datetime]

    chats: Mapped[list["DistributionChatORM"]] = relationship(
        back_populates="distribution"
    )

    is_active: Mapped[bool] = mapped_column(default=False)


class ModeratorORM(Adm, Base):
    __tablename__ = "moderator_table"

    chats: Mapped[list["ModeratorChatORM"]] = relationship(lazy="joined")


class ModeratorChatORM(Base):
    __tablename__ = "moderator_chat_table"

    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chat_table.id"))
    chat: Mapped["ChatORM"] = relationship(back_populates="moderators")
    moderator_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("moderator_table.id")
    )
    moderator: Mapped["ModeratorORM"] = relationship(back_populates="chats")

    # Права. При добавлении или удалении одного измените инлайн-клавиатуру изменения прав модератора
    ba_perm: Mapped[permission_tp]
    ban_perm: Mapped[permission_tp]
    kick_perm: Mapped[permission_tp]
    mute_perm: Mapped[permission_tp]
    warn_perm: Mapped[permission_tp]
    close_perm: Mapped[permission_tp]
    linkto_perm: Mapped[permission_tp]
    perm_perm: Mapped[permission_tp]

    updated_at: Mapped[updated_attp]

    repr_cols = "id"


@dataclass
class UserRest:

    user_id: Mapped[int] = mapped_column(BigInteger)

    by_moderator_id: Mapped[int] = mapped_column(BigInteger)
    chat_id: Mapped[Optional[int]] = mapped_column(BigInteger)


class BaRestORM(Base, UserRest):
    __tablename__ = "ba_rest_table"


class BanRestORM(Base, UserRest):
    __tablename__ = "ban_rest_table"


class MuteRestORM(Base, UserRest):
    __tablename__ = "mute_rest_table"
    period: Mapped[timedelta]


class WarnRestORM(Base, UserRest):
    __tablename__ = "warn_rest_table"
    reason: Mapped[Optional[str]]

class PassedCaptchaUserORM(Base):
    __tablename__ = 'passed_captcha_user_table'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

@dataclass
class BasePerm:
    can_send_messages: Mapped[bool]
    can_send_audios: Mapped[bool]
    can_send_documents: Mapped[bool]
    can_send_photos: Mapped[bool]
    can_send_videos: Mapped[bool]
    can_send_video_notes: Mapped[bool]
    can_send_voice_notes: Mapped[bool]
    can_send_polls: Mapped[bool]
    can_send_other_messages: Mapped[bool]
    can_add_web_page_previews: Mapped[bool]
    can_change_info: Mapped[bool]
    can_invite_users: Mapped[bool]
    can_pin_messages: Mapped[bool]
    can_manage_topics: Mapped[bool]

class UserPermORM(Base, BasePerm):
    __tablename__ = 'user_perm_table'

    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chat_table.id"))
    user_id: Mapped[int] = mapped_column(BigInteger)

class ChatPermORM(Base, BasePerm):
    __tablename__ = 'chat_perm_table'
    
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chat_table.id"))