from typing import TypeVar
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import ColumnExpressionArgument, select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_async_db
from src.api.v1 import models, schemas


class BaseRepository:
    _model = models.BaseModel
    _schema = schemas.Base
    _name: str = 'base'
    _session: AsyncSession

    def __init__(
            self,
            session: AsyncSession = Depends(get_async_db),
    ):
        self._session = session

    async def get(
            self,
            *where: ColumnExpressionArgument,
    ) -> list[schemas.TBaseSchema]:
        stmt = select(self._model).where(*where)  # type: ignore
        items = (await self._session.scalars(stmt))
        return [self._schema.model_validate(item) for item in items]

    async def get_by_id(self, obj_id: UUID) -> schemas.TBaseSchema:
        db_obj: models.BaseModel = (await self._session.get(self._model, obj_id))
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'{self._name} not found'
            )
        return self._schema.model_validate(db_obj)

    async def create(self, **kwargs) -> schemas.TBaseSchema:
        from src.api.v1 import models
        db_obj: models.BaseModel = self._model(**kwargs)
        try:
            self._session.add(db_obj)
            await self._session.commit()
            await self._session.refresh(db_obj)
        except IntegrityError:
            await self._session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'the {self._name} is duplicated'
            )
        except DatabaseError:
            await self._session.rollback()
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f'DB error while creating {self._name}'
            )
        # TODO write log if Exception

        return self._schema.model_validate(db_obj)

    async def update(self, obj_id: UUID, **kwargs) -> schemas.TBaseSchema:
        db_obj: models.BaseModel = (await self._session.get(self._model, obj_id))
        try:
            for column, value in kwargs.items():
                setattr(db_obj, column, value)
            await self._session.commit()
            await self._session.refresh(db_obj)
        except IntegrityError:
            await self._session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'the {self._name} is duplicated'
            )
        except DatabaseError:
            await self._session.rollback()
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f'DB error while update {self._name}'
            )
        # TODO write log if Exception

        return self._schema.model_validate(db_obj)

    async def delete(self, obj_id: UUID) -> None:
        db_obj: models.BaseModel = (await self._session.get(self._model, obj_id))
        try:
            await self._session.delete(db_obj)
            await self._session.commit()
        except DatabaseError:
            await self._session.rollback()
            raise HTTPException(
                status_code=status.HTTP_424_FAILED_DEPENDENCY,
                detail=f'DB error while deleting {self._name}'
            )
        # TODO write log if Exception

        return


TBaseRepository = TypeVar('TBaseRepository', bound=BaseRepository)
