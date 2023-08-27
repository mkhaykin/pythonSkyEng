from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.api.config import settings
from src.api.v1.db import fake_users_db
from src.api.v1.schemas import TokenData, User, UserInDB

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/token')


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not (user and verify_password(password, user.hashed_password)):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ACCESS_TOKEN_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ACCESS_TOKEN_ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise CREDENTIALS_EXCEPTION
        token_data = TokenData(username=username)
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    if not token_data.username:
        raise CREDENTIALS_EXCEPTION

    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user
