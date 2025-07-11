from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

from src.domain.model.training import Training as DomainTraining, Task as DomainTask, Validate as DomainValidate
from src.domain.ports.training_repository import TrainingRepository
from src.domain.exceptions import NotFoundError

class TrainingService:
    def __init__(self, repo: TrainingRepository):
        self._repo = repo

    def get_training(self, id: UUID) -> DomainTraining:
        training = self._repo.find_by_id(id)
        if not training:
            raise NotFoundError(f"Training {id} not found")
        return training
    
    def create_training(self, owner_id: UUID, name: str, description: str) -> DomainTraining:
        training = DomainTraining(
            id=uuid4(),
            owner_id=owner_id,
            name=name,
            description=description,
            created_at=datetime.utcnow()
        )
        return self._repo.add_training(training)
    
    def delete_training(self, id: UUID) -> None:
        training = self._repo.find_by_id(id)
        if not training:
            raise NotFoundError(f"Training {id} not found")
        self._repo.delete_training(id)
    
    def update_training(
        self,
        training_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> DomainTraining:
        training = self._repo.find_by_id(training_id)
        if not training:
            raise NotFoundError(f"Training {training_id} not found")

        if name is not None:
            training.name = name
        if description is not None:
            training.description = description

        return self._repo.update_training(training)
    
    def get_all_owner_trainings(self, owner_id: UUID) -> List[DomainTraining]:
        trainings = self._repo.find_all_owner_trainings(owner_id)
        if not trainings:
            return []
        return trainings
    
    
