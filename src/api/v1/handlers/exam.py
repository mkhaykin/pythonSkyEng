from fastapi import APIRouter, Depends

from src.api.v1.services import ExamService

router = APIRouter(
    prefix='/api/v1/exam'
)


@router.get('/check')
async def files1(
        service: ExamService = Depends(),
):
    return await service.check_all()


@router.get('/uncheck')
async def files2(
        service: ExamService = Depends(),
):
    return await service.uncheck()
