import os

from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.app import fastapi_app
from src.api.config import settings
from src.api.v1 import models
from src.api.v1.handlers import files


async def send_file(
        client: AsyncClient,
        token: str,
        path: str,
        filename: str,
        waited_code: int = status.HTTP_201_CREATED,
) -> dict[str, str]:
    response = await client.post(
        fastapi_app.url_path_for(files.upload.__name__),
        headers={'Authorization': f'Bearer {token}'},
        files={
            'file': (filename, open(os.path.join(path, filename), 'rb'), 'text/x-python')
        },
    )

    assert response.status_code == waited_code
    return response.json()


async def get_files(
        client: AsyncClient,
        token: str,
        waited_code: int = status.HTTP_200_OK,
) -> list[dict[str, str]]:
    response = await client.get(
        fastapi_app.url_path_for(files.files.__name__),
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == waited_code
    if response.status_code == status.HTTP_200_OK:
        # TODO assert для каждого элемента списка ?
        pass
    return response.json()


async def replace_file(
        client: AsyncClient,
        token: str,
        path: str,
        filename: str,
        file_id: str,
        waited_code: int = status.HTTP_200_OK,
) -> dict[str, str]:
    print(file_id)
    response = await client.patch(
        fastapi_app.url_path_for(files.replace_file.__name__, file_id=file_id),
        headers={'Authorization': f'Bearer {token}'},
        files={
            'file': (filename, open(os.path.join(path, filename), 'rb'), 'text/x-python')
        },
    )

    assert response.status_code == waited_code
    return response.json()


async def delete_file(
        client: AsyncClient,
        token: str,
        file_id: str,
        waited_code: int = status.HTTP_200_OK,
) -> dict[str, str]:
    response = await client.delete(
        fastapi_app.url_path_for(files.delete_file.__name__, file_id=file_id),
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == waited_code
    return response.json()


async def file_id_in_files(
        client: AsyncClient,
        token: str,
        file_id: str,
) -> bool:
    data: list[dict[str, str]] = await get_files(
        client=client,
        token=token,
    )
    return any([file_id == item.get('id') for item in data])


async def get_file_name(
        session: AsyncSession,
        file_id: str,
) -> str:
    db_file: models.Files = await session.get(models.Files, file_id)
    return db_file.name


async def file_in_store(
        filename: str,
) -> bool:
    filepath = os.path.join(
        settings.FILE_STORE_PATH,
        filename,
    )
    return os.path.isfile(filepath)


async def file_id_in_store(
        session: AsyncSession,
        file_id: str,
) -> bool:
    return await file_in_store(await get_file_name(session, file_id))
