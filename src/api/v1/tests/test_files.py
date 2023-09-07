import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1 import models

from .samlpe_users import USER_SARA, USER_TOM
from .test_utils_files import (
    delete_file,
    file_id_in_files,
    file_in_store,
    get_file_name,
    replace_file,
    send_file,
)
from .test_utils_user import get_user_token


@pytest.mark.asyncio
async def test_file_upload_ok(db_test_users: AsyncSession, async_client: AsyncClient):
    # получаем токен
    token: str = await get_user_token(async_client, USER_TOM)

    # загружаем файл
    data = await send_file(
        client=async_client,
        token=token,
        path='./src/api/',
        filename='app.py',
    )
    file_id: str = data.get('id', '')

    # проверяем, что виден
    assert await file_id_in_files(
        client=async_client,
        token=token,
        file_id=file_id,
    )

    # получаем физическое имя файла
    filename = await get_file_name(
        session=db_test_users,
        file_id=file_id,
    )

    # проверяем, что есть в файловом хранилище
    assert await file_in_store(filename)

    # удаляем
    await delete_file(
        client=async_client,
        token=token,
        file_id=file_id,
    )

    # проверяем, что не виден
    assert not await file_id_in_files(
        client=async_client,
        token=token,
        file_id=file_id,
    )

    # проверяем, что нет в файловом хранилище
    assert not (await file_in_store(filename))

    # повторно удаляем
    await delete_file(
        client=async_client,
        token=token,
        file_id=file_id,
        waited_code=404,
    )


@pytest.mark.asyncio
async def test_file_view_wrong_user(db_test_users: AsyncSession, async_client: AsyncClient):
    # получаем токен
    token_tom: str = await get_user_token(async_client, USER_TOM)
    token_sara: str = await get_user_token(async_client, USER_SARA)

    # загружаем файл
    data = await send_file(
        client=async_client,
        token=token_tom,
        path='./src/api/',
        filename='app.py',
    )
    file_id: str = data.get('id', '')

    # видим у Тома
    assert await file_id_in_files(
        client=async_client,
        token=token_tom,
        file_id=file_id,
    )

    # не видим у Сары
    assert not (await file_id_in_files(
        client=async_client,
        token=token_sara,
        file_id=file_id,
    ))

    # удаляем
    await delete_file(
        client=async_client,
        token=token_tom,
        file_id=file_id,
        waited_code=status.HTTP_200_OK,
    )


@pytest.mark.asyncio
async def test_file_put_wrong_user(db_test_users: AsyncSession, async_client: AsyncClient):
    # получаем токен
    token_tom: str = await get_user_token(async_client, USER_TOM)
    token_sara: str = await get_user_token(async_client, USER_SARA)

    _param_send = dict(
        client=async_client,
        path='./src/api/',
        filename='app.py',
    )
    # загружаем файл
    data = await send_file(
        token=token_tom,
        **_param_send,
    )
    file_id: str = data.get('id', '')

    _param_replace = dict(
        client=async_client,
        file_id=file_id,
        path='./src/api/',
        filename='config.py',
    )
    # не можем изменить под Сарой
    await replace_file(
        token=token_sara,
        waited_code=status.HTTP_401_UNAUTHORIZED,
        **_param_replace,
    )
    # меняем под Томом
    data = await replace_file(
        token=token_tom,
        waited_code=status.HTTP_200_OK,
        **_param_replace,
    )
    file2_id: str = data.get('id', '')

    db_file: models.Files

    # у первого должен быть установлен признак замены
    # проверяем прямо базу
    db_file = await db_test_users.get(models.Files, file_id)
    assert db_file.is_replaced

    _param1_del = dict(client=async_client, file_id=file_id)
    _param2_del = dict(client=async_client, file_id=file2_id)

    # не можем удалить первый файл
    await delete_file(
        token=token_tom,
        waited_code=status.HTTP_409_CONFLICT,
        **_param1_del,
    )

    # не можем удалить первый файл под Сарой
    # мы должны получить именно ошибку авторизации, а не ошибку "файл заменен"
    await delete_file(
        token=token_sara,
        waited_code=status.HTTP_401_UNAUTHORIZED,
        **_param1_del,
    )

    # удаляем второй файл под Томом
    await delete_file(
        token=token_tom,
        waited_code=status.HTTP_200_OK,
        **_param2_del,
    )

    # у первого признак замены должен быть снят
    await db_test_users.refresh(db_file)
    assert not db_file.is_replaced

    # удаляем первый файл под Томом
    await delete_file(
        token=token_tom,
        waited_code=status.HTTP_200_OK,
        **_param1_del,
    )


@pytest.mark.asyncio
async def test_file_delete_wrong_user(db_test_users: AsyncSession, async_client: AsyncClient):
    # получаем токен
    token_tom: str = await get_user_token(async_client, USER_TOM)
    token_sara: str = await get_user_token(async_client, USER_SARA)

    # загружаем файл
    data = await send_file(
        client=async_client,
        path='./src/api/',
        filename='app.py',
        token=token_tom,
    )
    file_id: str = data.get('id', '')

    # не можем удалить под Сарой
    await delete_file(
        client=async_client,
        token=token_sara,
        file_id=file_id,
        waited_code=status.HTTP_401_UNAUTHORIZED,
    )

    # можем удалить под Томом
    await delete_file(
        client=async_client,
        token=token_tom,
        file_id=file_id,
        waited_code=status.HTTP_200_OK,
    )


# проверить можно ли заменить замененное
@pytest.mark.asyncio
async def test_file_put_patched(db_test_users: AsyncSession, async_client: AsyncClient):
    # получаем токен
    token_tom: str = await get_user_token(async_client, USER_TOM)

    # загружаем файл
    data = await send_file(
        client=async_client,
        token=token_tom,
        path='./src/api/',
        filename='app.py',
    )
    file_id: str = data.get('id', '')

    data = await replace_file(
        client=async_client,
        token=token_tom,
        file_id=file_id,
        path='./src/api/',
        filename='config.py',
    )
    file2_id: str = data.get('id', '')

    await replace_file(
        client=async_client,
        token=token_tom,
        file_id=file_id,
        path='./src/api/',
        filename='config.py',
        waited_code=status.HTTP_409_CONFLICT,
    )

    await delete_file(
        client=async_client,
        token=token_tom,
        file_id=file2_id,
    )

    await delete_file(
        client=async_client,
        token=token_tom,
        file_id=file_id,
    )
