import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import ColumnExpressionArgument, select

from src.api.v1 import models, schemas
from src.api.v1.repositories.base import BaseRepository


class FilesRepository(BaseRepository):
    _model = models.Files
    _name = 'files'

    async def check(self, file_id: UUID, message: str):
        await self.update(
            obj_id=file_id,
            checked_at=datetime.datetime.utcnow(),
            checked_result=message,
        )

    async def _get(
            self,
            *where: ColumnExpressionArgument,
    ) -> list[schemas.FileInDB]:
        stmt = select(self._model).where(*where)
        items = (await self._session.scalars(stmt))
        return [schemas.FileInDB.model_validate(item) for item in items]

    async def get(
            self,
    ) -> list[schemas.FileInDB]:
        return await self._get()

    async def get_unchecked(
            self,
    ) -> list[schemas.FileInDB]:
        return await self._get(self._model.checked_at.is_(None))  # ignore

    async def get_by_user(self, user_id: UUID) -> list[schemas.FileInDB]:
        return await self._get(self._model.user_id == str(user_id))

    async def delete(self, obj_id: UUID) -> None:
        await super().delete(obj_id)

        # Убираем ссылки у замененных файлов
        # В теории должен быть один файл, но ...
        query = (
            select(
                models.Files.id,
            )
            .where(models.Files.replaced_id == obj_id)
        )

        db_file: models.Files
        try:
            for file_id in (await self._session.execute(query)):
                db_file = await self._session.get(models.Files, file_id)
                db_file.replace(None)
            await self._session.commit()
        except Exception:   # TODO DatabaseError:
            await self._session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,   # TODO 500?
                detail=f'DB error while deleting {self._name}')
            # TODO write log if Exception
