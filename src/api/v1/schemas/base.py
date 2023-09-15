from typing import TypeVar
from pydantic import BaseModel


class Base(BaseModel):
    pass


TBaseSchema = TypeVar('TBaseSchema', bound=Base)
