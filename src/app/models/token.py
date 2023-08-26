import datetime

import jwt

from src.app.api import API_URL_TOKEN_RENEWAL, API_URL_TOKEN_REQUEST, post

# запас времени, который мы даем на обработку истекающего токена
TOKEN_TIME_RESERVE: datetime.timedelta = datetime.timedelta(minutes=1)
# за какое время до истечения начинаем продлевать
TOKEN_TIME_RENEWAL: datetime.timedelta = datetime.timedelta(minutes=29)


def timestamp_utc():
    """ Текущий штамп времени по utc 0."""
    import datetime
    from datetime import timezone

    dt = datetime.datetime.now(timezone.utc)

    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    return utc_timestamp


def time_to_int(date: datetime.datetime):
    """ Перевод в int без учета часового пояса."""
    total = int(date.strftime('%S'))
    total += int(date.strftime('%M')) * 60
    total += int(date.strftime('%H')) * 60 * 60
    total += (int(date.strftime('%j')) - 1) * 60 * 60 * 24
    total += (int(date.strftime('%Y')) - 1970) * 60 * 60 * 24 * 365
    return total


class TokenInfo:
    _token: str
    _alg: str
    _typ: str
    _sub: str
    _exp: int
    _exp_utc: datetime.datetime

    def __init__(self, token: str):
        self._token = token
        self._alg = ''
        self._typ = ''
        self._sub = ''
        self._exp = 0
        self._exp_utc = datetime.datetime.utcfromtimestamp(int(self._exp))
        if token:
            self._decode()

    def _decode(self):
        header = jwt.get_unverified_header(self.token)
        self._alg = header['alg']
        self._typ = header['typ']
        body = jwt.decode(self.token, options={'verify_signature': False})
        self._sub = body['sub']
        self._exp = body['exp']
        self._exp_utc = datetime.datetime.utcfromtimestamp(int(self._exp))

    @property
    def token(self):
        return self._token

    @property
    def alg(self):
        return self._alg

    @property
    def typ(self):
        return self._typ

    @property
    def sub(self):
        return self._sub

    @property
    def exp(self):
        return self._exp

    @property
    def exp_utc(self):
        return self._exp_utc


def get_token(token: str) -> TokenInfo:
    obj_token = TokenInfo(token)
    return obj_token


def is_token_expired(token: str | None) -> bool:
    if not token:
        return True

    obj_token = TokenInfo(token)
    return obj_token.exp_utc <= datetime.datetime.utcnow() - TOKEN_TIME_RESERVE


def is_token_needs_updating(token: str):
    assert token
    obj_token = TokenInfo(token)
    return obj_token.exp_utc <= datetime.datetime.utcnow() + TOKEN_TIME_RENEWAL


def request_token(username: str, password: str) -> str | None:
    # TODO: write log "request_token"
    answer = post(
        url=API_URL_TOKEN_REQUEST,
        data={
            'username': username,
            'password': password
        }
    )
    if answer:
        return answer.json()['access_token']

    return None


def refresh_token(token: str) -> str | None:
    # TODO: write log "refresh_token"
    if token is None:
        return None

    answer = post(
        url=API_URL_TOKEN_RENEWAL,
        token=token,
    )
    if answer:
        return answer.json()['access_token']
    return None
