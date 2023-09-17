import datetime
import os
import shutil
import uuid
from uuid import UUID

from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.api.config import settings
from src.api.v1 import models, repositories, schemas

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/token')


class FilesService:
    _repo: repositories.FilesRepository

    def __init__(self, repo: repositories.FilesRepository = Depends()):
        self._repo = repo

    async def files(self, user_id: UUID) -> list[schemas.FileInDB]:
        return await self._repo.get_by_user(user_id)

    async def file(self, file_id: UUID, user_id: UUID) -> schemas.FileInDB:
        file: schemas.FileInDB = await self._repo.get_by_id(file_id)
        await self._check_owner(file, user_id)
        return file

    @staticmethod
    def _copy_to_store(file: UploadFile, filename: str):
        try:
            _file: str = os.path.join(settings.FILE_STORE_PATH, filename)
            with open(_file, 'wb') as f:
                shutil.copyfileobj(file.file, f)
        except Exception as e:
            print(e)  # TODO write to log
            return {'message': 'There was an error uploading the file'}
        finally:
            file.file.close()

    @staticmethod
    def check_file_extension(file: UploadFile):
        if file.content_type != 'text/x-python':
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Invalid document type')

    async def upload(self, file: UploadFile, user_id: UUID):
        self.check_file_extension(file)

        filename = str(uuid.uuid4()) + '.py'
        self._copy_to_store(file, filename)

        db_file: models.Files = await self._repo.create(
            name=filename,
            original_name=file.filename,
            user_id=user_id,
        )

        return db_file

    @staticmethod
    async def _check_owner(file: schemas.FileInDB, user_id: UUID):
        # TODO: is user an administrator?
        if file.user_id != user_id:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    async def _delete_from_store(filename: str):
        try:
            file: str = os.path.join(settings.FILE_STORE_PATH, filename)
            os.remove(file)
        except Exception as e:
            print(e)  # TODO write to log

    async def replace(self, file_id: UUID, file: UploadFile, user_id: UUID):
        self.check_file_extension(file)

        old_file: schemas.FileInDB = await self._repo.get_by_id(file_id)
        await self._check_owner(old_file, user_id)

        # TODO нельзя заменять уже замененное
        if old_file.is_replaced:
            raise HTTPException(status.HTTP_409_CONFLICT, 'File already replaced.')

        filename = str(uuid.uuid4())
        self._copy_to_store(file, filename)

        new_file: schemas.FileInDB = await self._repo.create(
            name=filename,
            original_name=file.filename,
            user_id=user_id,
        )

        # TODO сделать метод в репозитории
        await self._repo.update(
            obj_id=file_id,
            replaced_id=new_file.id,
            replaced_at=datetime.datetime.utcnow(),
        )

        return new_file

    async def delete(self, file_id: UUID, user_id: UUID):
        # TODO check exists?
        db_file: schemas.FileInDB = await self._repo.get_by_id(file_id)
        await self._check_owner(db_file, user_id)

        # нельзя удалять замененный файл, удаление с "вершины" дерева
        if db_file.is_replaced:
            raise HTTPException(status.HTTP_409_CONFLICT, 'This file is replaced.')

        await self._delete_from_store(filename=db_file.name)
        await self._repo.delete(file_id)

        return {'message': f'Successfully deleted {file_id}'}
