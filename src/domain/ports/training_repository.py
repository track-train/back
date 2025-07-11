from abc import abstractmethod, ABC
from src.domain.model.training import Training, Task, Validate
from typing import Optional, List
from uuid import UUID

class TrainingRepository(ABC):
    @abstractmethod
    def find_by_id(self, id:UUID) -> Optional[Training]:
        pass

    @abstractmethod
    def add_training(self, training: Training) -> Optional[Training]:
        pass

    @abstractmethod
    def delete_training(self, id: UUID) -> None:
        pass

    @abstractmethod
    def update_training(self, training: Training) -> Optional[Training]:
        pass

    @abstractmethod
    def find_all_owner_trainings(self, owner_id: UUID) -> Optional[List[Training]]:
        pass

