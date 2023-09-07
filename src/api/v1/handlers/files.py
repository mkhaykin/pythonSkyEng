from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status

from src.api.v1 import schemas
from src.api.v1.services import FilesService, get_current_active_user

router = APIRouter(
    prefix='/api/v1/files'
)


@router.get('/')
async def files(
        current_user: schemas.User = Depends(get_current_active_user),
        service: FilesService = Depends(),
):
    return await service.files(
        user_id=current_user.id,
    )


@router.get(
    path='/{file_id}',
)
async def file(
        file_id: UUID,
        current_user: schemas.User = Depends(get_current_active_user),
        service: FilesService = Depends(),
):
    return await service.file(
        file_id=file_id,
        user_id=current_user.id,
    )


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.FileId,
)
async def upload(
        file: UploadFile = File(...),
        current_user: schemas.User = Depends(get_current_active_user),
        service: FilesService = Depends(),
):
    return await service.upload(
        file=file,
        user_id=current_user.id,
    )


@router.patch(
    path='/{file_id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.FileId,
)
async def replace_file(
        file_id: UUID,
        file: UploadFile = File(...),
        current_user: schemas.User = Depends(get_current_active_user),
        service: FilesService = Depends(),
):
    print('replace')
    return await service.replace(
        file_id=file_id,
        file=file,
        user_id=current_user.id,
    )


@router.delete(
    path='/{file_id}',
)
async def delete_file(
        file_id: UUID,
        current_user: schemas.User = Depends(get_current_active_user),
        service: FilesService = Depends(),
):
    return await service.delete(
        file_id=file_id,
        user_id=current_user.id,
    )
