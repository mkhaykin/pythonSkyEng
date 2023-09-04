from sqlalchemy.engine import URL

from src.api.config import settings

_db_params = {
    'username': settings.POSTGRES_USER,
    'password': settings.POSTGRES_PASSWORD,
    'host': settings.POSTGRES_HOST,
    'port': settings.POSTGRES_PORT,
    'database': settings.POSTGRES_DB,
}

_test_db_params = _db_params.copy()
_test_db_params['database'] = str(_test_db_params['database']) + '_test'

SQLALCHEMY_DATABASE_URL = URL.create(
    drivername='postgresql',
    **_db_params,
)

SQLALCHEMY_DATABASE_URL_async = URL.create(
    drivername='postgresql+asyncpg',
    **_db_params,
)

SQLALCHEMY_TEST_DATABASE_URL = URL.create(
    drivername='postgresql',
    **_test_db_params,
)

SQLALCHEMY_TEST_DATABASE_URL_async = URL.create(
    drivername='postgresql+asyncpg',
    **_test_db_params,
)
