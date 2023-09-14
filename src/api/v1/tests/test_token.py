from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.config import settings
from src.jwt_token import TokenInfo

from .samlpe_users import USER_JOHN, USER_SARA, USER_TOM
from .test_utils_user import get_token, registry


@pytest.mark.asyncio
async def test_token_ok(async_db: AsyncSession, async_client: AsyncClient):
    await registry(
        async_client,
        **USER_TOM,
        waited_code=status.HTTP_201_CREATED)

    data = await get_token(
        async_client,
        identity=USER_TOM['username'],
        password=USER_TOM['password'],
        waited_code=status.HTTP_201_CREATED)

    obj_token = TokenInfo(data['access_token'])
    # check token subject
    assert obj_token.sub == USER_TOM['username']
    # check token time
    time_before = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES - 1)
    time_after = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1)
    assert time_before <= obj_token.exp_utc
    assert obj_token.exp_utc <= time_after


@pytest.mark.asyncio
async def test_token_case(async_db_clear: AsyncSession, async_client: AsyncClient):
    await registry(
        async_client,
        **USER_TOM,
        waited_code=status.HTTP_201_CREATED)

    data = await get_token(
        async_client,
        identity=USER_TOM['username'].upper(),
        password=USER_TOM['password'],
        waited_code=status.HTTP_201_CREATED)

    obj_token = TokenInfo(data['access_token'])
    # check token subject
    assert obj_token.sub == USER_TOM['username']


@pytest.mark.asyncio
async def test_token_unauthorised_user_wrong_password(async_db: AsyncSession, async_client: AsyncClient):
    await registry(
        async_client,
        **USER_JOHN,
        waited_code=status.HTTP_201_CREATED)

    await get_token(
        async_client,
        identity=USER_JOHN['username'],
        password='wrong_password',
        waited_code=status.HTTP_401_UNAUTHORIZED)


@pytest.mark.asyncio
async def test_token_unauthorised_user_not_exist(async_db: AsyncSession, async_client: AsyncClient):
    await get_token(
        async_client,
        identity=USER_SARA['username'],
        password=USER_SARA['password'],
        waited_code=status.HTTP_401_UNAUTHORIZED)
