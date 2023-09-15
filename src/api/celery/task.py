import asyncio

from src.api.config import settings
from src.api.database import AsyncSession, ping_db
from src.api.v1.repositories import FilesRepository
from src.api.v1.services import ExamService

from .app import app_celery


async def async_check_files():
    async with AsyncSession() as session:
        if not (await ping_db(session)):
            print('database not available')  # TODO write to log
            return

        try:
            repo = FilesRepository(session)
            service = ExamService(repo)
            await service.check()
        except Exception as e:
            print(e)    # TODO write log


@app_celery.task
def check_files():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_check_files())


@app_celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        settings.EXAM_SCHEDULE,
        check_files.s(),
        name='task complete',
    )
