from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, computed_field

from .base import Base


class _File(Base):
    name: str
    original_name: str
    replaced_id: UUID | None
    replaced_at: datetime | None
    checked_at: datetime | None
    checked_result: str | None
    send_result_at: datetime | None


class _FileId(Base):
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

    @computed_field   # type: ignore
    @property
    def is_replaced(self) -> bool:
        return bool(self.replaced_at)

    @computed_field   # type: ignore
    @property
    def is_checked(self) -> bool:
        return bool(self.checked_at)

    @computed_field   # type: ignore
    @property
    def is_result_sent(self) -> bool:
        return bool(self.send_result_at)

    model_config = ConfigDict(
        from_attributes=True,
    )
