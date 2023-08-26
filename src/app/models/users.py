import datetime
import uuid

from flask_login import UserMixin

from src.app import db
from src.app.models.token import (
    TokenInfo,
    is_token_expired,
    is_token_needs_updating,
    refresh_token,
    request_token,
)


class Users(UserMixin, db.Model):
    id = db.Column(
        'id',
        db.Text(length=36),
        default=lambda: str(uuid.uuid4()),
        primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)

    token = db.Column(db.String, nullable=True)
    token_alg = db.Column(db.String, nullable=True)
    token_typ = db.Column(db.String, nullable=True)
    token_sub = db.Column(db.String, nullable=True)
    token_exp = db.Column(db.Integer, nullable=True)
    token_exp_utc = db.Column(db.DateTime, nullable=True)

    created_on = db.Column(db.DateTime, default=lambda: datetime.datetime.now(), nullable=False)

    def __init__(self, username: str):
        self.username = username

    def set_token(self, token: TokenInfo):
        self.token = token.token
        self.token_alg = token.alg
        self.token_typ = token.typ
        self.token_sub = token.sub
        self.token_exp = token.exp
        self.token_exp_utc = token.exp_utc

    @staticmethod
    def get_by_name(username: str) -> 'Users':
        return db.session.execute(db.select(Users).filter_by(username=username)).scalar()

    @staticmethod
    def get_by_id(user_id: str) -> 'Users':
        return db.session.execute(db.select(Users).filter_by(id=user_id)).scalar()

    def is_token_expired(self):
        return not self.token or is_token_expired(self.token)

    def is_token_needs_updating(self):
        assert self.token
        return is_token_needs_updating(self.token)

    def request_token(self, password: str):
        # TODO: write log
        print('Users.request_token')
        res = request_token(self.username, password)
        if res:
            self.set_token(TokenInfo(res))
            db.session.commit()

    def refresh_token(self):
        # TODO: write log
        print('Users.refresh_token')
        token = refresh_token(self.token)
        if token:
            self.set_token(TokenInfo(token))
            db.session.commit()
