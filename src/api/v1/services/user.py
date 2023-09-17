from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.api.config import settings
from src.api.v1 import repositories, schemas
from src.api.v1.services.token import create_access_token

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/token')


class UserService:
    _repo: repositories.UserRepository

    def __init__(self, repo: repositories.UserRepository = Depends()):
        self._repo = repo

    @staticmethod
    def _check_password(password: str, password_hash: str):
        return pwd_context.verify(password, password_hash)

    async def new_user_registration(self, user: schemas.UserRegistration) -> schemas.UserInDB:
        user.email = user.email.lower()
        return await self._repo.create(**user.model_dump())

    @staticmethod
    def _create_token(username: str, email: str = '') -> schemas.TokenModel:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={'sub': username, 'email': email}, expires_delta=access_token_expires
        )
        return schemas.TokenModel(**{'access_token': access_token, 'token_type': 'bearer'})

    async def token_request(self, identifier: str, password: str) -> schemas.TokenModel:
        user = await self._repo.get_user(identifier)

        if not user or not self._check_password(password, user.psw_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return self._create_token(user.username, user.email)

    def token_renewal(self, user: schemas.User) -> schemas.TokenModel:
        return self._create_token(user.username, user.email)
