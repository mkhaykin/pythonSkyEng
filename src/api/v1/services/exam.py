import os

from fastapi import Depends

from src.api.config import settings
from src.api.v1 import repositories, schemas


class ExamService:
    _repo: repositories.FilesRepository

    def __init__(self, repo: repositories.FilesRepository = Depends()):
        self._repo = repo

    async def check(self):
        items: list[schemas.FileInDB] = await self._repo.get_unchecked()
        for item in items:
            file = os.path.join(settings.FILE_STORE_PATH, item.name)
            if os.path.isfile(file):
                message = os.popen(f'pre-commit run --files {file}').read()
                await self._repo.check(item.id, message)
            else:
                # TODO write log
                print(f'file {file} not found')
                pass
        return {'detail': 'check complete'}

    async def uncheck(self):
        pass
