import datetime
import uuid

from flask import abort
from flask_api import status
from flask_login import UserMixin, logout_user

from src.app import db
from src.app.api.request import post
from src.app.api.urls import API_URL_TOKEN_RENEWAL, API_URL_TOKEN_REQUEST
from src.jwt_token import TokenInfo

# запас времени, который мы даем на обработку истекающего токена
TOKEN_TIME_RESERVE: datetime.timedelta = datetime.timedelta(seconds=10)
# за какое время до истечения начинаем продлевать
TOKEN_TIME_RENEWAL: datetime.timedelta = datetime.timedelta(minutes=29)


class Users(UserMixin, db.Model):
    id = db.Column(
        'id',
        db.Text(length=36),
        default=lambda: str(uuid.uuid4()),
        primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)

    token = db.Column(db.String, nullable=True)
    token_alg = db.Column(db.String, nullable=True)
    token_typ = db.Column(db.String, nullable=True)
    token_sub = db.Column(db.String, nullable=True)
    token_exp = db.Column(db.Integer, nullable=True)
    token_exp_utc = db.Column(db.DateTime, nullable=True)

    created_on = db.Column(db.DateTime, default=lambda: datetime.datetime.now(), nullable=False)

    def __init__(
            self,
            username: str,
            email: str,
    ):
        self.username = username
        self.email = email

    def set_token(self, token: str):
        obj_token: TokenInfo = TokenInfo(token)
        self.token = obj_token.token
        self.token_alg = obj_token.alg
        self.token_typ = obj_token.typ
        self.token_sub = obj_token.sub
        self.token_exp = obj_token.exp
        self.token_exp_utc = obj_token.exp_utc

    @staticmethod
    def get_by_identity(identity: str) -> 'Users':
        return db.session.execute(
            db.select(Users).where((Users.username == identity) | (Users.email == identity))
        ).scalar()

    @staticmethod
    def get_by_id(user_id: str) -> 'Users':
        return db.session.execute(db.select(Users).filter_by(id=user_id)).scalar()

    def is_token_expired(self):
        return not self.token or (self.token_exp_utc <= datetime.datetime.utcnow() - TOKEN_TIME_RESERVE)

    def is_token_needs_updating(self):
        return self.token_exp_utc <= datetime.datetime.utcnow() + TOKEN_TIME_RENEWAL

    def request_token(self, password: str):
        # TODO: write log
        answer = post(
            url=API_URL_TOKEN_REQUEST,
            data={
                'username': self.username,
                'password': password
            }
        )
        if not answer:
            abort(status.HTTP_503_SERVICE_UNAVAILABLE, 'api call error')
        elif answer.status_code == status.HTTP_401_UNAUTHORIZED:
            abort(status.HTTP_401_UNAUTHORIZED, 'no such user or password')
        elif answer.status_code == status.HTTP_200_OK:
            res = answer.json()['access_token']
            if res:
                self.set_token(res)
                db.session.commit()
        # TODO status something wrong

    def refresh_token(self):
        # TODO: write log
        if self.token is None:
            return None

        answer = post(
            url=API_URL_TOKEN_RENEWAL,
            token=self.token,
        )
        if not answer:
            # если не можем обновить, то просто пропускаем событие
            return
        elif answer.status_code == status.HTTP_401_UNAUTHORIZED:
            logout_user()
            # TODO очистка токена
            return

        token = answer.json().get('access_token')
        if token:
            self.set_token(token)
            db.session.commit()
