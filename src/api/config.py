from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    POSTGRES_HOST: str = '127.0.0.1'
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = ''
    POSTGRES_USER: str = ''
    POSTGRES_PASSWORD: str = ''

    SECRET_KEY: str = ''
    ACCESS_TOKEN_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    FILE_STORE_PATH: str = ''

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
