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

# tasks abstract methods

    @abstractmethod
    def add_task(self, task: Task) -> Optional[Task]:
        pass

    @abstractmethod
    def find_task_by_id(self, id: UUID) -> Optional[Task]:
        pass

    @abstractmethod
    def delete_task(self, id: UUID) -> None:
        pass

    @abstractmethod
    def update_task(self, task: Task) -> Optional[Task]:
        pass

    @abstractmethod
    def find_tasks_by_training_id(self, training_id: UUID) -> Optional[List[Task]]:
        pass

# validate abstract methods

    @abstractmethod
    def add_validate(self, validate: Validate) -> Optional[Validate]:
        pass

    @abstractmethod
    def find_validate_by_task_id(self, id: UUID) -> Optional[Validate]:
        pass

    @abstractmethod
    def delete_validate(self, id: UUID) -> None:
        pass

    @abstractmethod
    def find_validate_by_id(self, id: UUID) -> Optional[Validate]:
        pass

    @abstractmethod
    def find_all_validates_by_training_id(self, training_id: UUID) -> Optional[List[Validate]]:
        pass

