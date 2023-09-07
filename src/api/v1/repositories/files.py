from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_async_db
from src.api.v1 import models
from src.api.v1.repositories.base import BaseRepository


class FilesRepository(BaseRepository):
    _model: type[models.Files]

    def __init__(
            self,
            session: AsyncSession = Depends(get_async_db),
    ):
        super().__init__(session)
        self._name = 'files'
        self._model = models.Files

    async def get_by_user(self, user_id: UUID) -> list[models.Files]:
        query = (
            select(
                models.Files.id,
                models.Files.original_name,

                models.Files.replaced_id,
                models.Files.replaced_at,

                models.Files.checked_at,
                models.Files.checking_result,

                models.Files.send_result_at,
            )
            .where(models.Files.user_id == user_id)
        )
        db_files = (await self._session.execute(query)).mappings().all()
        return db_files

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
                # db_file.replaced_id = None
                # db_file.replaced_at = None
            await self._session.commit()
        except Exception:   # TODO DatabaseError:
            await self._session.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'DB error while deleting {self._name}')
        # TODO write log if Exception
