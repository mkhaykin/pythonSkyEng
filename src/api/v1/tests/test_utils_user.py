from httpx import AsyncClient

from src.api.app import fastapi_app
from src.api.v1.handlers.routes import create_user_registration, login_for_access_token


async def registry(
        client: AsyncClient,
        username: str,
        email: str,
        password: str,
        waited_code: int = 201,
) -> dict:
    response = await client.post(
        fastapi_app.url_path_for(create_user_registration.__name__),
        json={
            'username': username,
            'email': email,
            'password': password,
        }
    )
    assert response.status_code == waited_code
    data = response.json()
    if waited_code == 201:
        assert 'username' in data
        assert 'email' in data

        assert data['username'] == username
        assert data['email'] == email
    return data


async def get_token(
        client: AsyncClient,
        identity: str,
        password: str,
        waited_code: int = 201,
) -> dict[str, str]:
    response = await client.post(
        fastapi_app.url_path_for(login_for_access_token.__name__),
        data={
            'username': identity,
            'password': password,
        }
    )
    assert response.status_code == waited_code
    data = response.json()
    if waited_code == 200:
        assert 'access_token' in data
        assert 'token_type' in data
        assert data['token_type'] == 'bearer'

    return data
