from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.v1.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from src.api.config import settings
from src.api.v1.db import fake_users_db
from src.api.v1.schemas import TokenModel, User

router = APIRouter(
    prefix='/api/v1'
)


@router.get(
    path='/'
)
async def health_check():
    return {'message': 'I\'m fine'}


@router.post(
    path='/token',
    response_model=TokenModel
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post(
    path='/token_renewal',
    response_model=TokenModel,
)
async def login_for_renewal_token(current_user: User = Depends(get_current_active_user)):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': current_user.username}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


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
