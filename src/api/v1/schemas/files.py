from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class _File(BaseModel):
    name: str
    original_name: str
    replaced_id: UUID | None
    replaced_at: datetime | None
    checked_at: datetime | None
    checked_result: str | None
    send_result_at: datetime | None


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


class FileInDB(_FileId, _File):
    created_at: datetime
    updated_at: datetime | None

    user_id: UUID

    model_config = ConfigDict(
        from_attributes=True,
    )
