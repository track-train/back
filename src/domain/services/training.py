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
    
    # tasks methods service
    
    def create_task(
        self,
        training_id: UUID,
        exercise_name: str,
        rest_time: Optional[int] = None,
        repetitions: Optional[int] = None,
        set_number: Optional[int] = None,
        method: Optional[str] = None,
        rir: Optional[int] = None,
    ) -> DomainTask:
        training = self._repo.find_by_id(training_id)
        if not training:
            raise NotFoundError(f"Training {training_id} not found")
        if not exercise_name:
            raise ValueError("Exercise name is required")

        task = DomainTask(
            id=uuid4(),
            training_id=training_id,
            exercise_name=exercise_name,
            rest_time=rest_time,
            repetitions=repetitions,
            set_number=set_number,
            method=method,
            rir=rir,
            updated_at=datetime.utcnow(),
            validate=[],             
        )

        return self._repo.add_task(task)


    def get_task(self, task_id: UUID) -> DomainTask:
        task = self._repo.find_task_by_id(task_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found")
        return task


    def update_task(
        self,
        task_id: UUID,
        exercise_name: Optional[str] = None,
        rest_time: Optional[int] = None,
        repetitions: Optional[int] = None,
        set_number: Optional[int] = None,
        method: Optional[str] = None,
        rir: Optional[int] = None,
    ) -> DomainTask:
        task = self._repo.find_task_by_id(task_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found")
        
        if exercise_name is not None:
            task.exercise_name = exercise_name
        if rest_time is not None:
            task.rest_time = rest_time
        if repetitions is not None:
            task.repetitions = repetitions
        if set_number is not None:
            task.set_number = set_number
        if method is not None:
            task.method = method
        if rir is not None:
            task.rir = rir

        return self._repo.update_task(task)


    def delete_task(self, task_id: UUID) -> None:
        task = self._repo.find_task_by_id(task_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found")

        self._repo.delete_task(task_id)


    def list_tasks_for_training(self, training_id: UUID) -> List[DomainTask]:
        tasks = self._repo.find_tasks_by_training_id(training_id)
        if tasks is None:
            return []
        return tasks
    
    # validate methods service

    def create_validate(
        self,
        task_id: UUID,
        rest_time: Optional[int] = None,
        repetitions: Optional[int] = None,
        set_number: Optional[int] = None,
        rir: Optional[int] = None,
    ) -> DomainValidate:
        task = self._repo.find_task_by_id(task_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found")

        validate = DomainValidate(
            id=uuid4(),
            task_id=task_id,
            exercise_name=task.exercise_name,  # Assuming exercise_name is needed
            rest_time=rest_time,
            repetitions=repetitions,
            set_number=set_number,
            rir=rir,
            updated_at=datetime.utcnow(),
            succeeded_at=datetime.utcnow(),  # This can be set later when validation is successful
        )

        return self._repo.add_validate(validate)

    def get_validates_for_task(self, task_id: UUID) -> List[DomainValidate]:
        validates = self._repo.find_validate_by_task_id(task_id)
        if not validates:
            return []
        return validates

    def delete_validate(self, validate_id: UUID) -> None:
        validate = self._repo.find_validate_by_id(validate_id)
        if not validate:
            raise NotFoundError(f"Validation {validate_id} not found")
        self._repo.delete_validate(validate_id)

    def get_validate_by_training_id(self, training_id: UUID) -> List[DomainValidate]:
        if not self._repo.find_by_id(training_id):
          raise NotFoundError(f"Training {training_id} not found")
        return self._repo.find_all_validates_by_training_id(training_id)