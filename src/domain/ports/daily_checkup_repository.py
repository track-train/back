from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from src.domain.model.daily_checkup import DailyCheckup

class DailyCheckupRepository(ABC):
    @abstractmethod
    async def add(self, daily_checkup: DailyCheckup) -> DailyCheckup:
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[DailyCheckup]:
        pass

    @abstractmethod
    async def find_by_profile_id(self, profile_id: UUID) -> List[DailyCheckup]:
        pass

    @abstractmethod
    async def find_by_profile_id_and_date(self, profile_id: UUID, date: str) -> Optional[DailyCheckup]:
        pass

    @abstractmethod
    async def update(self, daily_checkup: DailyCheckup) -> DailyCheckup:
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        pass