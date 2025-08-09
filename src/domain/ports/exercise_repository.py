from abc import abstractmethod, ABC
from src.domain.model.exercise import Exercise
from typing import Optional, List
from uuid import UUID

class ExerciseRepository(ABC):
    @abstractmethod
    async def add(self, exercise: Exercise) -> Optional[Exercise]:
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        pass

    @abstractmethod
    async def update(self, exercise: Exercise) -> Optional[Exercise]:
        pass

    @abstractmethod
    async def find_all_owner(self, owner_id: UUID) -> Optional[List[Exercise]]:
        pass

    @abstractmethod
    async def find_all(self) -> Optional[List[Exercise]]:
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[Exercise]:
        pass