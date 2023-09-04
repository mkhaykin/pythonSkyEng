from typing import TypeVar
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_async_db
from src.api.v1 import models


class BaseRepository:
    _name: str = 'base'
    _model: type[models.BaseModel]
    _session: AsyncSession

    def __init__(
            self,
            session: AsyncSession = Depends(get_async_db),
    ):
        self._model = models.BaseModel
        self._session = session

    async def get_by_id(self, obj_id: UUID) -> models.TBaseModel:
        db_obj: models.BaseModel = (await self._session.get(self._model, obj_id))
        if not db_obj:
            raise HTTPException(404, f'{self._name} not found')
        return db_obj

    async def create(self, **kwargs) -> models.TBaseModel:
        from src.api.v1 import models
        db_obj: models.BaseModel = self._model(**kwargs)
        try:
            self._session.add(db_obj)
            await self._session.commit()
            await self._session.refresh(db_obj)
        except IntegrityError:
            await self._session.rollback()
            raise HTTPException(409, f'the {self._name} is duplicated')
        except DatabaseError:
            await self._session.rollback()
            raise HTTPException(424, f'DB error while creating {self._name}')
        # TODO write log if Exception
        return db_obj

    async def update(self, obj_id: UUID, **kwargs) -> models.TBaseModel:
        db_obj: models.BaseModel = (await self.get_by_id(obj_id))
        try:
            for column, value in kwargs.items():
                setattr(db_obj, column, value)
            await self._session.commit()
            await self._session.refresh(db_obj)
        except IntegrityError:
            await self._session.rollback()
            raise HTTPException(409, f'the {self._name} is duplicated')
        except DatabaseError:
            await self._session.rollback()
            raise HTTPException(424, f'DB error while update {self._name}')
        # TODO write log if Exception

        return db_obj

    async def delete(self, obj_id: UUID) -> None:
        db_obj: models.BaseModel = await self.get_by_id(obj_id)
        try:
            await self._session.delete(db_obj)
            await self._session.commit()
        except DatabaseError:
            await self._session.rollback()
            raise HTTPException(424, f'DB error while deleting {self._name}')
        # TODO write log if Exception

        return


TBaseRepository = TypeVar('TBaseRepository', bound=BaseRepository)
