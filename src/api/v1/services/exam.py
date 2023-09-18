import os
from uuid import UUID

from fastapi import Depends, HTTPException, status

from src.api.config import settings
from src.api.v1 import repositories, schemas


class ExamService:
    _repo: repositories.FilesRepository

    def __init__(self, repo: repositories.FilesRepository = Depends()):
        self._repo = repo

    async def check_all(self) -> schemas.Message:
        items: list[schemas.FileInDB] = await self._repo.get_unchecked()
        for item in items:
            await self.check(item)
        return schemas.Message(detail='check complete')  # TODO more info

    async def check_by_id(self, file_id: UUID) -> schemas.Message:
        item: schemas.FileInDB = await self._repo.get_by_id(file_id)
        if item:
            await self.check(item)
        else:
            HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return schemas.Message(detail='check complete')   # TODO more info

    async def check(self, file: schemas.FileInDB) -> None:
        fullpath: str = os.path.join(settings.FILE_STORE_PATH, file.name)
        if os.path.isfile(fullpath):
            message = os.popen(f'pre-commit run --files {fullpath}').read()
            await self._repo.check(file.id, message)
        else:
            # TODO write log
            print(f'file {fullpath} not found')
            pass

    async def uncheck(self) -> None:
        pass
