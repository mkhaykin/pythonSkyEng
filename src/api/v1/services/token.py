from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.api.config import settings
from src.api.v1.models import Users
from src.api.v1.repositories import UserRepository
from src.api.v1.schemas import User

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/token')


def create_access_token(
        data: dict,
        expires_delta: timedelta = timedelta(minutes=15),
) -> str:
    to_encode = data.copy()
    to_encode.update({'exp': datetime.utcnow() + expires_delta})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ACCESS_TOKEN_ALGORITHM
    )


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        repo: UserRepository = Depends(),
) -> Users:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ACCESS_TOKEN_ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    user = await repo.get_user(username)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user
