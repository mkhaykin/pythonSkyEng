from src.api.app import fastapi_app
from src.api.v1.handlers.routes import (
    create_user_registration,
    login_for_access_token,
    login_for_renewal_token,
    read_own_items,
    read_users_me,
)

API_HOST = '127.0.0.1'
API_PORT = 8000
API_URL = f'http://{API_HOST}:{API_PORT}'

API_URL_TOKEN_REQUEST = API_URL + fastapi_app.url_path_for(login_for_access_token.__name__)
API_URL_TOKEN_RENEWAL = API_URL + fastapi_app.url_path_for(login_for_renewal_token.__name__)
API_URL_USER_REGISTRATION = API_URL + fastapi_app.url_path_for(create_user_registration.__name__)
# API_URL_USER_REGISTRATION = 'http://127.0.0.1:8001/api/v1/'
API_URL_ME = API_URL + fastapi_app.url_path_for(read_users_me.__name__)
API_URL_STAT = API_URL + fastapi_app.url_path_for(read_own_items.__name__)
