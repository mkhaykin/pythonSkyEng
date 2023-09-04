from httpx import AsyncClient

from src.api.app import fastapi_app
from src.api.v1.handlers.routes import create_user_registration


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
