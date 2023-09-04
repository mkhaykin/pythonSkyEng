from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.config import settings
from src.token import TokenInfo

from .samlpe_users import user_john, user_sara, user_tom
from .test_utils_user import get_token, registry


@pytest.mark.asyncio
async def test_token_ok(async_db: AsyncSession, async_client: AsyncClient):
    await registry(
        async_client,
        **user_tom,
        waited_code=201)

    data = await get_token(
        async_client,
        identity=user_tom['username'],
        password=user_tom['password'],
        waited_code=200)

    obj_token = TokenInfo(data['access_token'])
    # check token subject
    assert obj_token.sub == user_tom['username']
    # check token time
    time_before = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES - 1)
    time_after = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)
    assert time_before <= obj_token.exp_utc
    assert obj_token.exp_utc <= time_after


@pytest.mark.asyncio
async def test_token_unauthorised_user_wrong_password(async_db: AsyncSession, async_client: AsyncClient):
    await registry(
        async_client,
        **user_john,
        waited_code=201)

    await get_token(
        async_client,
        identity=user_john['username'],
        password='wrong_password',
        waited_code=401)


@pytest.mark.asyncio
async def test_token_unauthorised_user_not_exist(async_db: AsyncSession, async_client: AsyncClient):
    await get_token(
        async_client,
        identity=user_sara['username'],
        password=user_sara['password'],
        waited_code=401)
