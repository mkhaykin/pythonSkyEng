from typing import AsyncGenerator

# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext import asyncio
from sqlalchemy.orm import sessionmaker

from src.api.database.urls import SQLALCHEMY_DATABASE_URL_async
from src.api.v1.models import Base

async_engine = asyncio.create_async_engine(
    SQLALCHEMY_DATABASE_URL_async,
    pool_pre_ping=True,
    # echo=True,
    # echo=settings.db_echo_log,
    future=True,
)


AsyncSession = sessionmaker(  # type: ignore
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=asyncio.AsyncSession,
    expire_on_commit=False
)


async def get_async_db() -> AsyncGenerator:
    async with AsyncSession() as session:
        yield session


async def async_create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def async_drop_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
