from abc import abstractmethod, ABC
from src.domain.model.exercise import Exercise
from typing import Optional, List
from uuid import UUID

class ExerciseRepository(ABC):
    @abstractmethod
    def add(self, exercise: Exercise) -> Optional[Exercise]:
        pass

    @abstractmethod
    def delete(self, id: UUID) -> None:
        pass

    @abstractmethod
    def update(self, exercise: Exercise) -> Optional[Exercise]:
        pass

    @abstractmethod
    def find_all_owner(self, owner_id: UUID) -> Optional[List[Exercise]]:
        pass

    @abstractmethod
    def find_all(self) -> Optional[List[Exercise]]:
        pass

    @abstractmethod
    def find_by_id(self, id: UUID) -> Optional[Exercise]:
        pass