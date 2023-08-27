from sqlalchemy import Column, String, UniqueConstraint

from src.api.v1.models.base import Base
from src.api.v1.models.mixin_id import MixinID
from src.api.v1.models.mixin_ts import MixinTimeStamp


class Users(Base, MixinID, MixinTimeStamp):
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    psw_hash = Column(String, primary_key=True, nullable=False)

    __table_args__ = (
        UniqueConstraint('username', name='uc_username'),
        UniqueConstraint('email', name='uc_email'),
    )
