from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime

from src.domain.model.training import Training as DomainTraining, Task as DomainTask, Validate as DomainValidate
from src.domain.ports.training_repository import TrainingRepository
from src.domain.exceptions import NotFoundError

class InMemoryTrainingRepository(TrainingRepository):
    def __init__(self):
        self._trainings: dict[UUID, DomainTraining] = {}
        self._tasks: dict[UUID, DomainTask] = {}
        self._validates: dict[UUID, DomainValidate] = {}

    # Training methods
    def find_by_id(self, id: UUID) -> Optional[DomainTraining]:
        return self._trainings.get(id)

    def add_training(self, training: DomainTraining) -> DomainTraining:
        new_id = uuid4()
        training.id = new_id
        if not getattr(training, 'created_at', None):
            training.created_at = datetime.utcnow()
        self._trainings[new_id] = training
        return training

    def delete_training(self, id: UUID) -> None:
        self._trainings.pop(id, None)
        for task_id, task in list(self._tasks.items()):
            if task.training_id == id:
                self.delete_task(task_id)

    def update_training(self, training: DomainTraining) -> Optional[DomainTraining]:
        if training.id not in self._trainings:
            raise NotFoundError(f"Training {training.id} not found")
        self._trainings[training.id] = training
        return training

    def find_all_owner_trainings(self, owner_id: UUID) -> List[DomainTraining]:
        return [t for t in self._trainings.values() if t.owner_id == owner_id]

    # Task methods
    def add_task(self, task: DomainTask) -> DomainTask:
        new_id = uuid4()
        task.id = new_id
        if not getattr(task, 'updated_at', None):
            task.updated_at = datetime.utcnow()
        self._tasks[new_id] = task
        return task

    def find_task_by_id(self, id: UUID) -> Optional[DomainTask]:
        return self._tasks.get(id)

    def delete_task(self, id: UUID) -> None:
        task = self._tasks.pop(id, None)
        if task:
            for vid, validate in list(self._validates.items()):
                if validate.task_id == id:
                    self.delete_validate(vid)

    def update_task(self, task: DomainTask) -> Optional[DomainTask]:
        if task.id not in self._tasks:
            raise NotFoundError(f"Task {task.id} not found")
        self._tasks[task.id] = task
        return task

    def find_tasks_by_training_id(self, training_id: UUID) -> List[DomainTask]:
        return [t for t in self._tasks.values() if t.training_id == training_id]

    # Validate methods
    def add_validate(self, validate: DomainValidate) -> DomainValidate:
        new_id = uuid4()
        validate.id = new_id
        if not getattr(validate, 'succeeded_at', None):
            validate.succeeded_at = datetime.utcnow()
        self._validates[new_id] = validate
        return validate

    def find_validate_by_id(self, id: UUID) -> Optional[DomainValidate]:
        return self._validates.get(id)

    def find_validate_by_task_id(self, task_id: UUID) -> List[DomainValidate]:
        return [v for v in self._validates.values() if v.task_id == task_id]

    def find_all_validates_by_training_id(self, training_id: UUID) -> List[DomainValidate]:
        task_ids = {t.id for t in self._tasks.values() if t.training_id == training_id}
        return [v for v in self._validates.values() if v.task_id in task_ids]

    def delete_validate(self, id: UUID) -> None:
        self._validates.pop(id, None)
