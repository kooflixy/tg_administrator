import datetime
from typing import Annotated
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import settings

database_url_asyncpg = f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}'

async_engine = create_async_engine(
    url = database_url_asyncpg
)

async_session_factory = async_sessionmaker(async_engine)


intpk = Annotated[int, mapped_column(primary_key=True)]
created_attp = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_attp = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=text("TIMEZONE('utc', now())")
    )]

class Base(DeclarativeBase):
    id: Mapped[intpk]
    created_at: Mapped[created_attp]
    
    repr_cols_num = 2
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f'{col}={getattr(self, col)}')
        
        return f'<{self.__class__.__name__} {','.join(cols)}>'
