from uuid import UUID

from pydantic import BaseModel


class _File(BaseModel):
    username: str
    email: str
    disabled: bool = False


class _FileId(BaseModel):
    id: UUID


class File(_File):
    pass


class FileId(_FileId):
    pass


class FileReplace(_FileId):
    pass


class FileDelete(_FileId):
    pass
