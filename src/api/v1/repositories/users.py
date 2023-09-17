from fastapi import HTTPException
from sqlalchemy import Result, or_, select
from sqlalchemy.exc import NoResultFound

from src.api.v1 import models, schemas

# from src.api.v1.models import Users
from src.api.v1.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    _model = models.Users
    _schema = schemas.UserInDB
    _name = 'user'

    def verify_user(self, username: str, email: str) -> bool:
        """
        Проверяем есть уникальность имени / почты
        :param username_or_email:
        :return:
        """
        # TODO
        return True

    async def get_user(self, username_or_email: str) -> schemas.UserInDB | None:
        username_or_email = username_or_email.lower()
        stmt = (
            select(
                models.Users  # type: ignore
            ).where(
                or_(
                    models.Users.name == username_or_email,
                    models.Users.email == username_or_email,
                )
            )
        )

        try:
            result: Result = (await self._session.scalars(stmt))
            db_user = result.one()
        except ConnectionRefusedError:
            # TODO write and send log
            raise HTTPException(
                status_code=500,
                detail='Internal Server Database Error',
            )
        except NoResultFound:
            return None
        # except Exception:
        #     # TODO write log
        #     return None

        return schemas.UserInDB.model_validate(db_user)

