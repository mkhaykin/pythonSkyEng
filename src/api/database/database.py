from typing import AsyncGenerator

from sqlalchemy import select, text
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.api.database.urls import SQLALCHEMY_DATABASE_URL, SQLALCHEMY_DATABASE_URL_async
from src.api.v1.models import Base

_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    # echo=True,
    # echo=settings.db_echo_log,
)

_Session = sessionmaker(_engine)


def get_db(session=_Session):
    db = session()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=_engine)


def drop_tables():
    Base.metadata.drop_all(bind=_engine)


_async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL_async,
    pool_pre_ping=True,
    # echo=True,
    # echo=settings.db_echo_log,
    future=True,
)


_AsyncSession = sessionmaker(  # type: ignore
    bind=_async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def ping_db(session: AsyncSession) -> bool:
    try:
        await session.execute(select(text('1')))
    except Exception:
        # TODO write to log
        return False

    return True


async def get_async_db() -> AsyncGenerator:
    async with _AsyncSession() as session:
        yield session


async def async_create_tables():
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def async_drop_tables():
    async with _async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
