import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from src.api.v1.models.base import Base
from src.api.v1.models.mixin_id import MixinID
from src.api.v1.models.mixin_ts import MixinTimeStamp


class Files(Base, MixinID, MixinTimeStamp):
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    name = Column(String, unique=True, index=True, nullable=False)
    original_name = Column(String, unique=False, index=True, nullable=False)

    replaced_id = Column(UUID(as_uuid=True), index=True, nullable=True)
    replaced_at = Column(DateTime(timezone=True))

    checked_at = Column(DateTime(timezone=True))
    checked_result = Column(String, unique=False, nullable=True, server_default='')

    send_result_at = Column(DateTime(timezone=True))

    @property
    def is_replaced(self) -> bool:
        return bool(self.replaced_at)

    @property
    def is_checked(self) -> bool:
        return bool(self.checked_at)

    @property
    def is_result_sent(self) -> bool:
        return bool(self.send_result_at)

    def __init__(self, name: str, original_name: str, user_id: UUID):
        super().__init__()
        self.name = name
        self.original_name = original_name
        self.user_id = user_id

    def replace(self, with_id: UUID | None):
        self.replaced_id = with_id
        if with_id:
            self.replaced_at = datetime.datetime.now()
        else:
            self.replaced_at = None

    def check_completed(self, message: str):
        self.checked_result = message
        self.checked_at = datetime.datetime.now()

    def result_sent(self):
        self.send_result_at = datetime.datetime.now()

    __table_args__ = (
        UniqueConstraint('name', name='uc_name'),
    )
