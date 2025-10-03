from datetime import datetime
from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

T = TypeVar("T")


class Pagination(BaseModel):
    page: int
    size: int
    total: int


class Paginated(GenericModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int


class Timestamped(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
