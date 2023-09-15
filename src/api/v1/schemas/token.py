from .base import Base


class TokenModel(Base):
    access_token: str
    token_type: str


class TokenData(Base):
    username: str | None = None
