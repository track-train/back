from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.exceptions import NotFoundError

from src.adapters.sqlalchemy.models import Exercise as ORMExercise, Training as ORMTraining, Task as ORMTask
from src.domain.model.training import Validate as DomainValidate, Task as DomainTask, Training as DomainTraining
from src.domain.ports.training_repository import TrainingRepository
from uuid import UUID


def validate_from_orm(orm_validate) -> DomainValidate:
    return DomainValidate(
        id=orm_validate.id,
        task_id=orm_validate.task_id,
        rest_time=orm_validate.rest_time,
        repetitions=orm_validate.repetitions,
        set_number=orm_validate.set_number,
        rir=orm_validate.rir,
        updated_at=orm_validate.updated_at,
        succeeded_at=orm_validate.succeeded_at,
    )

def task_from_orm(orm_task) -> DomainTask:
    return DomainTask(
        id=orm_task.id,
        training_id=orm_task.training_id,
        exercise_id=orm_task.exercise_id,
        rest_time=orm_task.rest_time,
        repetitions=orm_task.repetitions,
        set_number=orm_task.set_number,
        method=orm_task.method,
        rir=orm_task.rir,
        updated_at=orm_task.updated_at,
        validate=[validate_from_orm(v) for v in orm_task.validations] if orm_task.validations else None,
    )

def training_from_orm(orm_training) -> DomainTraining:
    return DomainTraining(
        id=orm_training.id,
        owner_id=orm_training.owner_id,
        name=orm_training.name,
        description=orm_training.description,
        created_at=orm_training.created_at,
    )

class SqlAlchemyTrainingRepository(TrainingRepository):
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, id: UUID) -> Optional[DomainTraining]:
        orm = self._session.get(ORMTraining, id)
        return training_from_orm(orm) if orm else None
    

    # CRUD operations for Training
    def add_training(self, training: DomainTraining) -> Optional[DomainTraining]:
        data = training.to_orm_dict()
        orm = ORMTraining(**data)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return training_from_orm(orm) if orm else None
    
    def delete_training(self, id: UUID) -> None:
        orm = self._session.get(ORMTraining, id)
        if not orm:
            return
        self._session.delete(orm)
        self._session.commit()
    
    def update_training(self, training: DomainTraining) -> Optional[DomainTraining]:
        orm = self._session.get(ORMTraining, training.id)
        if not orm:
            raise NotFoundError(f"Training {training.id} not found")
        for key, value in training.to_orm_dict().items():
            setattr(orm, key, value)
        self._session.commit()
        return training_from_orm(orm) if orm else None
    
    def find_all_owner_trainings(self, owner_id: UUID) -> Optional[List[DomainTraining]]:
        orms = self._session.query(ORMTraining).filter(ORMTraining.owner_id == owner_id).all()
        return [training_from_orm(orm) for orm in orms] if orms else []
    

