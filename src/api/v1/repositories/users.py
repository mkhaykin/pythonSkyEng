from fastapi import Depends, HTTPException
from sqlalchemy import Result, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.database import get_async_db
from src.api.v1 import models
from src.api.v1.models import Users
from src.api.v1.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    _model: type[models.Users]

    def __init__(
            self,
            session: AsyncSession = Depends(get_async_db),
    ):
        super().__init__(session)
        self._name = 'user'
        self._model = models.Users

    def verify(self, username: str, email: str) -> bool:
        """
        Проверяем есть уникальность имени / почты
        :param username_or_email:
        :return:
        """
        # TODO
        return True
    # async def find_user(self, username_or_email: str) -> UUID:
    #     await self._session.get(Users)
    #     stmt = (
    #         select(
    #             Users.id,
    #         ).where(
    #             or_(
    #                 Users.username == username_or_email,
    #                 Users.email == username_or_email
    #             )
    #         )
    #     )
    #     result: Result = (await self._session.execute(stmt))
    #     db_user = result.one()

    async def get_user(self, username_or_email: str) -> Users | None:
        username_or_email = username_or_email.lower()
        stmt = (
            select(
                Users
            ).where(
                or_(
                    Users.name == username_or_email,
                    Users.email == username_or_email,
                    # 1 == 1,
                )
            )
        )

        try:
            result: Result = (await self._session.scalars(stmt))
            db_user = result.one_or_none()
        except ConnectionRefusedError:
            # TODO write and send log
            raise HTTPException(
                status_code=500,
                detail='Internal Server Database Error',
            )
        # except Exception:
        #     # TODO write log
        #     return None

        return db_user
