from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TEntity = TypeVar("TEntity")
TId = TypeVar("TId", bound=str)

class BaseRepository(ABC, Generic[TEntity, TId]):
    @abstractmethod
    async def create(self, entity: TEntity) -> TEntity: ...

    @abstractmethod
    async def get_by_id(self, id: TId) -> TEntity | None: ...

    @abstractmethod
    async def delete(self, id: TId) -> None: ...
