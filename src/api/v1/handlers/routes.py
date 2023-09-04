from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.v1 import schemas
from src.api.v1.schemas import TokenModel, User
from src.api.v1.services import UserService
from src.api.v1.services.token import get_current_active_user

router = APIRouter(
    prefix='/api/v1'
)


@router.get(
    path='/'
)
async def health_check():
    return {'message': 'I\'m fine'}


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.User,
)
async def create_user_registration(
        user: schemas.UserRegistration,
        service: UserService = Depends(),
):
    return await service.new_user_registration(user)


@router.post(
    path='/token',
    response_model=TokenModel,
)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        service: UserService = Depends(),
):
    return await service.token_request(form_data.username, form_data.password)


@router.post(
    path='/token_renewal',
    response_model=TokenModel,
)
async def login_for_renewal_token(
        user: User = Depends(get_current_active_user),
        service: UserService = Depends(UserService),
):
    return service.token_renewal(user)


@router.get(
    path='/me/',
    response_model=User,
)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get(
    path='/stat/',
)
async def read_own_items():
    return {
        'users': 100500,
        'all_tasks': 100,
        'verified_tasks': 50,
    }
