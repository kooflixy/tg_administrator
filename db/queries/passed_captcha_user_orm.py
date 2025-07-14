from logging import getLogger
from typing import Optional

from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatORM, PassedCaptchaUserORM
from db.queries import BaseORMHandler

log = getLogger(__name__)


class PassedCaptchaUserORMHandler(BaseORMHandler[PassedCaptchaUserORM]):
    model_cls = PassedCaptchaUserORM
    use_unique_scalars = False

    async def insert(session: AsyncSession, user_id: int) -> PassedCaptchaUserORM:
        obj = PassedCaptchaUserORM(id=user_id)
        session.add(obj)
