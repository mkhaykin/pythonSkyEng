from typing import TypeVar

from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase, configure_mappers, declared_attr

from .mixin_id import MixinID
from .mixin_ts import MixinTimeStamp


class Base(DeclarativeBase):
    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class BaseModel(Base, MixinID, MixinTimeStamp):
    __abstract__ = True

    @classmethod
    def __declare_last__(cls):
        super().__declare_last__()


TBaseModel = TypeVar('TBaseModel', bound=BaseModel)


@event.listens_for(Base.metadata, 'before_create')
def _configure_mappers(*args, **kwargs):
    configure_mappers()


from sqlalchemy import Column, String, UniqueConstraint


class TMPUSER(Base):
    username = Column(String, primary_key=True, unique=True, nullable=False)
