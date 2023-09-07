from http import HTTPStatus

from src.app import db
from src.app.api import get, post
from src.app.api.urls import (
    API_URL_ME,
    API_URL_TOKEN_REQUEST,
    API_URL_USER_REGISTRATION,
)
from src.app.exceptions import (
    TokenRequestException,
    UserCreateDuplicateException,
    UserCreateValuesException,
)
from src.app.models import Users


class UserService:

    @classmethod
    def request_user(cls, token: str) -> dict[str, str]:
        answer = get(
            url=API_URL_ME,
            token=token,
            data=None,
        )
        return answer.json()

    @classmethod
    def request_token(cls, identity: str, password: str) -> str:
        answer = post(
            url=API_URL_TOKEN_REQUEST,
            data={
                'username': identity,
                'password': password,
            }
        )
        if answer.status_code != HTTPStatus.CREATED or not answer.json() or not answer.json().get('access_token'):
            raise TokenRequestException()

        return answer.json()['access_token']

    @classmethod
    def register(cls, username: str, email: str, password: str) -> None:
        answer = post(
            url=API_URL_USER_REGISTRATION,
            json={
                'username': username,
                'email': email,
                'password': password,
            }
        )

        if answer.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            errors: dict[str, list[str]] = {}
            for item in answer.json().get('detail'):
                for key in ['username', 'email', 'password']:
                    if key in item.get('loc', []):
                        errors.setdefault(key, []).append(item.get('msg'))
            raise UserCreateValuesException(errors)
        elif answer.status_code == HTTPStatus.CONFLICT:
            raise UserCreateDuplicateException()

        return None

    @classmethod
    def login(cls, identity, password) -> Users:
        # запрашиваем токен всегда
        token = cls.request_token(identity, password)

        # запрашиваем пользовательские данные
        user: dict[str, str] = cls.request_user(token)
        username = user.get('username', '')
        email = user.get('email', '')
        if not (identity.lower() == username.lower() or identity.lower() == email.lower()):
            raise TokenRequestException('wrong username or email in token info')

        db_user: Users = Users.get_by_identity(identity=identity)
        if not db_user:
            db_user = Users(username=username, email=email)
            db.session.add(db_user)
        else:
            db_user.username = username
            db_user.email = email
        db_user.set_token(token)
        db.session.commit()

        return db_user
