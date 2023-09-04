from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.api.config import settings
from src.api.v1 import models, schemas
from src.api.v1.repositories import UserRepository

# from src.api.v1.schemas import TokenModel, User
from src.api.v1.services.token import create_access_token

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/token')


class UserService:
    _repo: UserRepository

    def __init__(self, repo: UserRepository = Depends()):
        self._repo = repo

    async def new_user_registration(self, user: schemas.UserRegistration) -> schemas.UserInDB:
        # user = await validator.verify_email_exist(request.email, database)
        # if user:
        #     raise HTTPException(
        #         status_code=400,
        #         detail="The user with this email already exists in the system.",
        #     )
        #
        db_user: models.Users = await self._repo.create(**user.model_dump())

        return schemas.UserInDB.model_validate(db_user)

    @staticmethod
    def _create_token(username: str, email: str = '') -> schemas.TokenModel:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={'sub': username, 'email': email}, expires_delta=access_token_expires
        )
        return schemas.TokenModel(**{'access_token': access_token, 'token_type': 'bearer'})

    async def token_request(self, identifier: str, password: str) -> schemas.TokenModel:
        user = await self._repo.get_user(identifier)

        if not user or not user.verify_password(password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password',
                headers={'WWW-Authenticate': 'Bearer'},
            )

        return self._create_token(user.username, user.email)

    def token_renewal(self, user: schemas.User) -> schemas.TokenModel:
        return self._create_token(user.username, user.email)
