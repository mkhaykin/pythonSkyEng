from pydantic import BaseModel as Base

from src.api.v1.schemas.token import (
    TokenModel,
    TokenData,
)

from src.api.v1.schemas.user import (
    User,
    UserInDB,
    UserRegistration,
)

from src.api.v1.schemas.files import (
    FileInDB,
    File,
    FileId,
    FileReplace,
    FileDelete,
)
