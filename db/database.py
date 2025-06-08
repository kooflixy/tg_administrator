import datetime
from typing import Annotated
from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from config import settings # должен быть импорт именно из config.config, иначе ImportError (circular import)


sync_engine = create_engine(
    url = settings.DATABASE_URL_psycopg
)

async_engine = create_async_engine(
    url = settings.DATABASE_URL_asyncpg
)

session_factory = sessionmaker(sync_engine)
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
