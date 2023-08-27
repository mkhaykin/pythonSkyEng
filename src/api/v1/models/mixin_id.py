from uuid import uuid4

from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import UUID


class MixinID:
    id = Column(UUID(as_uuid=True), server_default=func.gen_random_uuid(), primary_key=True, default=uuid4,
                nullable=False, )
