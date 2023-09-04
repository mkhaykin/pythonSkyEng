import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .test_utils_user import registry

user_sara = {
    'username': 'sara',
    'email': 'sara@sample.com',
    'password': 'SaraPassword$1',
}

user_tom = {
    'username': 'tom',
    'email': 'tom@sample.com',
    'password': 'TomPassword$1',
}


async def duplicate_user(async_client: AsyncClient, user1: dict, user2: dict):
    await registry(
        async_client,
        **user1,
        waited_code=201)

    data = await registry(
        async_client,
        **user2,
        waited_code=409)
    assert data == {'detail': 'the user is duplicated'}


@pytest.mark.asyncio
async def test_registry_ok(async_db_clear: AsyncSession, async_client: AsyncClient):
    await registry(
        async_client,
        **user_tom,
        waited_code=201)


@pytest.mark.asyncio
async def test_registry_duplicate_full(async_db_clear: AsyncSession, async_client: AsyncClient):
    await duplicate_user(async_client, user_tom, user_tom)


@pytest.mark.asyncio
async def test_registry_duplicate_name_case(async_db_clear: AsyncSession, async_client: AsyncClient):
    user1 = user_tom.copy()
    user1['username'] = user1['username'].lower()
    user2 = user_tom.copy()
    user2['username'] = user2['username'].upper()
    user2['email'] += '.random'
    await duplicate_user(async_client, user1, user2)


@pytest.mark.asyncio
async def test_registry_duplicate_email(async_db_clear: AsyncSession, async_client: AsyncClient):
    user1 = user_tom.copy()
    user1['email'] = user1['email'].lower()
    user2 = user_tom.copy()
    user2['username'] += '_random'
    user2['email'] = user2['email'].upper()
    await duplicate_user(async_client, user1, user2)


@pytest.mark.asyncio
@pytest.mark.parametrize('username', ['a', 'aa', 'a' * 33])
async def test_registry_wrong_name_size(async_db: AsyncSession, async_client: AsyncClient, username):
    user = user_tom.copy()
    user['username'] = username
    data = await registry(
        async_client,
        **user,
        waited_code=422)

    assert data['detail'][0]['type'] == 'value_error'
    assert data['detail'][0]['msg'] == 'Value error, username length must be between 3 and 32'


@pytest.mark.asyncio
@pytest.mark.parametrize('username', ['m@ya.ru', 'aaa#', 'aaa%', 'aaaa;'])
async def test_registry_wrong_symbol(async_db: AsyncSession, async_client: AsyncClient, username):
    user = user_tom.copy()
    user['username'] = username
    data = await registry(
        async_client,
        **user,
        waited_code=422)

    assert data['detail'][0]['type'] == 'value_error'
    assert data['detail'][0]['msg'] == 'Value error, only characters a-Z, 0-9, . and _ are allowed'


@pytest.mark.asyncio
@pytest.mark.parametrize('email', ['', 'm@ya.', '@ya.ru', 'm@ya.ru.', 'm@ya@ya.ru'])
async def test_registry_wrong_email(async_db: AsyncSession, async_client: AsyncClient, email):
    user = user_tom.copy()
    user['email'] = email
    data = await registry(
        async_client,
        **user,
        waited_code=422)

    assert data['detail'][0]['type'] == 'value_error'
    assert data['detail'][0]['msg'] == 'Value error, email is not a correct email address'


@pytest.mark.asyncio
@pytest.mark.parametrize('password', ['_' * i for i in range(8)])
async def test_registry_password_wrong_size(async_db: AsyncSession, async_client: AsyncClient, password):
    user = user_tom.copy()
    user['password'] = password
    data = await registry(
        async_client,
        **user,
        waited_code=422)

    assert data['detail'][0]['type'] == 'value_error'
    assert data['detail'][0]['msg'] == 'Value error, password length must be between 8 and 128'


# strong password
@pytest.mark.asyncio
@pytest.mark.parametrize('password', [
    '12345678',
    'qwertyui',
    'ASDFGHJK'
    'Aa1234567',
])
async def test_registry_password_not_strong(async_db: AsyncSession, async_client: AsyncClient, password):
    user = user_tom.copy()
    user['password'] = password
    data = await registry(
        async_client,
        **user,
        waited_code=422)

    assert data['detail'][0]['type'] == 'value_error'
    assert data['detail'][0]['msg'] == 'Value error, password does not meet security requirements'


@pytest.mark.asyncio
@pytest.mark.parametrize('password', [
    'Q1q!2345',
    'asdfgH1_',
])
async def test_registry_password_ok(async_db_clear: AsyncSession, async_client: AsyncClient, password):
    user = user_tom.copy()
    user['password'] = password
    await registry(
        async_client,
        **user,
        waited_code=201)
