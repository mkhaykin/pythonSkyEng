import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from src.api.app import fastapi_app as app
from src.api.database import (
    SQLALCHEMY_TEST_DATABASE_URL,
    SQLALCHEMY_TEST_DATABASE_URL_async,
    get_async_db,
)
from src.api.v1.models import Base

engine_test_async = create_async_engine(
    SQLALCHEMY_TEST_DATABASE_URL_async,
    pool_pre_ping=True
)

TestingSession = sessionmaker(
    bind=engine_test_async,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def override_get_async_db() -> AsyncGenerator:
    async with TestingSession() as session:
        yield session


async def create_tables_async():
    async with engine_test_async.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables_async():
    async with engine_test_async.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# @pytest_asyncio.fixture(scope='module')
# async def db_prod() -> AsyncGenerator:
#     app.dependency_overrides[get_db] = get_db
#     yield TestingSession()


@pytest.fixture(scope='session')
def create_db():
    if not database_exists(SQLALCHEMY_TEST_DATABASE_URL):
        create_database(SQLALCHEMY_TEST_DATABASE_URL)
    yield
    drop_database(SQLALCHEMY_TEST_DATABASE_URL)


# drop all database every time when test complete
@pytest_asyncio.fixture(scope='module')
async def async_db_engine(create_db):
    app.dependency_overrides[get_async_db] = override_get_async_db
    await drop_tables_async()
    await create_tables_async()

    yield engine_test_async


@pytest_asyncio.fixture(scope='module')
async def async_db(async_db_engine):
    async with TestingSession() as session:
        yield session


@pytest_asyncio.fixture(scope='function')
async def async_db_clear(async_db):
    await drop_tables_async()
    await create_tables_async()

    yield async_db


@pytest_asyncio.fixture(scope='module')
async def async_client() -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url='http://test') as client:
            yield client


# let test session to know it is running inside event loop
@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# @pytest_asyncio.fixture(scope='function')
# async def db_test_data(async_db):
#     async_db.add(Menus(**MENU1))
#     async_db.add(Menus(**MENU2))
#     await async_db.commit()
#     async_db.add(SubMenus(**SUBMENU1))
#     async_db.add(SubMenus(**SUBMENU2))
#     async_db.add(SubMenus(**SUBMENU3))
#     await async_db.commit()
#     async_db.add(Dishes(**DISH1))
#     async_db.add(Dishes(**DISH2))
#     async_db.add(Dishes(**DISH3))
#     await async_db.commit()
#
#     await cache_reset()
#     yield async_db
