from abc import ABC, abstractmethod
from logging import getLogger
from typing import Generic, Optional, Type, TypeVar, Union
from sqlalchemy import desc, select, text, delete
from sqlalchemy.ext.asyncio import AsyncSession

from config.changeable_config import changeable_settings
from db.database import Base

log = getLogger()

ModelType = TypeVar('ModelType', bound=Base)

class BaseORMHandler(Generic[ModelType], ABC):
    model_cls: Type[ModelType]
    use_unique_scalars: bool
    
    
    @classmethod
    def _get_unique_scalars(cls, obj) -> Union[Optional[ModelType], list[Optional[ModelType]]]:
        '''Делает скаляр ответа бд, в случае необходимости'''
        if cls.use_unique_scalars:
            obj = obj.unique()
        return obj


    @classmethod
    async def get(cls, session: AsyncSession, pk_value: int) -> Optional[ModelType]:
        '''Получает одну определенную запись по pk_value'''
        try:
            obj = await session.get(cls.model_cls, pk_value)
        except Exception as ex:
            log.error('При получении %s с pk_value=%s произошла ошибка', cls.model_cls, pk_value, exc_info=ex)
            raise ex
        
        return obj


    @classmethod
    async def _get_all(cls, session: AsyncSession, query) -> list[Optional[ModelType]]:
        '''Получает все существующие записи по выбранным настройкам. Является утилитой
        Желательно обставлять в try-except для более подробных логов'''
        result = await session.execute(query)
        scalars = result.scalars()
        obj_list = cls._get_unique_scalars(scalars)
        obj_list = scalars.all()
        
        return obj_list

    @classmethod
    async def get_all(cls, session: AsyncSession, query) -> list[Optional[ModelType]]:
        '''Получает все существующие записи'''
        query = (
            select(cls.model_cls)
        )

        try:
            return await cls._get_all(session, query)
        except Exception as ex:
            log.error('При получении всех %s произошла ошибка', cls.model_cls, exc_info=ex)
            raise ex

    @classmethod
    async def get_all_id(cls, session: AsyncSession) -> list[Optional[ModelType]]:
        '''Получает все существующие записи'''
        query = (
            select(cls.model_cls.id)
        )

        try:
            return await cls._get_all(session, query)
        except Exception as ex:
            log.error('При получении всех id %s произошла ошибка', cls.model_cls, exc_info=ex)
            raise ex
    

    @staticmethod
    def _excert_page_result(query, page: int, page_objs_count: int):
        '''Приеняется к объекту Query из sqlalchemy, выбирает записи для определенной страницы'''
        query = (
            query
            .offset(page_objs_count * (page-1))
            .limit(page_objs_count)
        )
        return query


    @classmethod
    async def _get_page(cls, session: AsyncSession, page: int, query) -> list[Optional[ModelType]]:
        '''Метод, получающий записи для определенной страницы с выбранными параметрами
        query должен быть запросом на список записей. Является утилитой
        Желательно обставлять в try-except для более подробных логов'''
        if not isinstance(page, int):
            raise TypeError('page должен быть int')

        query = cls._excert_page_result(query, page, changeable_settings.max_count_in_page)

        obj_list = await session.execute(query)
        obj_list = cls._get_unique_scalars(obj_list.scalars())
        obj_list = obj_list.all()
        return obj_list

    @classmethod
    async def get_page(cls, session: AsyncSession, page: int) -> list[Optional[ModelType]]:
        '''Получает страницу записей. Может переопределяться в дочерних классах'''
        query = (
            select(cls.model_cls)
            .order_by(desc(cls.model_cls.created_at), desc(cls.model_cls.id))
        )

        try:
            return await cls._get_page(session=session, page=page, query=query)
        except Exception as ex:
            log.error('При получении страницы %s произошла ошибка, page=%r', cls.model_cls, page, exc_info=ex)
            raise ex


    @classmethod
    async def _insert(cls, session: AsyncSession, **kwargs) -> ModelType:
        '''Служит утилитой'''
        obj = cls.model_cls(**kwargs)
        session.add(obj)
        return obj
    
    @classmethod
    @abstractmethod
    async def insert(cls, session: AsyncSession, **kwargs) -> ModelType:
        '''Абстрактый метод, реализуйте с использованием _insert()'''

    @classmethod
    async def remove(cls, session: AsyncSession, pk_value) -> None:
        '''Удаляет выбранную запись'''
        query = (
            delete(cls.model_cls)
            .filter(cls.model_cls.id==pk_value)
        )
        try:
            await session.execute(query)
        except Exception as ex:
            log.error('При удалении %r с pk_value=%r произошла ошибка', cls.model_cls, pk_value, exc_info=True)
            raise ex


    @classmethod
    async def _is_last_page(cls, session: AsyncSession, page: int, query) -> bool:
        '''Получает булево значение, является ли страница последней
        query должен быть запросом на список записей.  Является утилитой
        Желательно обставлять в try-except для более подробных логов'''
        if not isinstance(page, int):
            raise TypeError('page должен быть int')
        
        records_num = (await session.execute(query)).scalar()

        if records_num-changeable_settings.max_count_in_page*page<=0:
            return True
        return False
    
    @classmethod
    async def is_last_page(cls, session: AsyncSession, page: int) -> bool:
        '''Получает булево значение, является ли страница последней. Может переопределяться в дочерних классах'''
        query = text(f'SELECT COUNT(*) FROM {cls.model_cls.__tablename__}')
        
        try:
            return await cls._is_last_page(session=session, page=page, query=query)
        except Exception as ex:
            log.error('При попытке узнать последняя ли страница, произошла ошибка model=%r, page=%r', cls.model_cls, page, exc_info=True)
            raise ex