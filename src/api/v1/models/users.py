from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, String, UniqueConstraint

from src.api.v1.models.base import Base
from src.api.v1.models.mixin_id import MixinID
from src.api.v1.models.mixin_ts import MixinTimeStamp

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class Users(Base, MixinID, MixinTimeStamp):
    name = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    psw_hash = Column(String, nullable=False)
    disabled = Column(Boolean, nullable=False, default=False, server_default='f')

    __table_args__ = (
        UniqueConstraint('username', name='uc_username'),
        UniqueConstraint('email', name='uc_email'),
    )

    def __init__(self, **kwargs):
        # _ = kwargs.setdefault('name', kwargs.get('username', '').lower())
        if 'name' not in kwargs:
            kwargs['name'] = kwargs.get('username', '').lower()

        if 'password' in kwargs:
            self.set_password(kwargs.pop('password'))

        super().__init__(**kwargs)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.psw_hash)

    def set_password(self, password: str):
        self.psw_hash = pwd_context.hash(password)
