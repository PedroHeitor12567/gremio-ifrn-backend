from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.entities.impression import Impression


class ImpressionRepository(ABC):

    @abstractmethod
    async def save(self, impression: Impression) -> Impression:
        pass

    @abstractmethod
    async def find_by_id(self, impression_id: UUID) -> Optional[Impression]:
        pass

    @abstractmethod
    async def find_all(self) -> list[Impression]:
        pass

    @abstractmethod
    async def find_by_period(self, start: datetime, end: datetime) -> list[Impression]:
        pass

    @abstractmethod
    async def delete(self, impression_id: UUID) -> bool:
        pass
