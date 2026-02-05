from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar

class RequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

class ResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

T = TypeVar("T")

class PaginationParams(RequestSchema):
    page: int = 1
    page_size: int = 20

class PaginatedResponse(ResponseSchema, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int