import enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Annotated, Literal, Optional

from sqlalchemy import BigInteger, Boolean, ForeignKey, Interval
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.classes import ActionTypeEnum
from db.database import Base, updated_attp

permission_tp = Annotated[bool, mapped_column(default=False)]


class Adm:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str]


class ChatORM(Adm, Base):
    __tablename__ = "chat_table"

    moderators: Mapped[list["ModeratorChatORM"]] = relationship(lazy="joined")


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

    # Права
    ba_perm: Mapped[permission_tp]
    ban_perm: Mapped[permission_tp]
    kick_perm: Mapped[permission_tp]
    mute_perm: Mapped[permission_tp]
    warn_perm: Mapped[permission_tp]
    close_perm: Mapped[permission_tp]

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


class DistributionsORM(Base):
    __tablename__ = "distribution_table"

    chat_id: Mapped[int] = mapped_column(BigInteger)
    interval: Mapped[timedelta]
    next_dist_date: Mapped[datetime]