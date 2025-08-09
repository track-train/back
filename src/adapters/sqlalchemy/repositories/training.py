from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.domain.exceptions import NotFoundError

from src.adapters.sqlalchemy.models import Training as ORMTraining, Task as ORMTask, Validation as ORMValidate
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
        exercise_name=orm_task.exercise_name,
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
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def find_by_id(self, id: UUID) -> Optional[DomainTraining]:
        async with self._session_factory() as session:
            orm = await session.get(ORMTraining, id)
            return training_from_orm(orm) if orm else None
    
    # CRUD operations for Training
    async def add_training(self, training: DomainTraining) -> Optional[DomainTraining]:
        data = training.to_orm_dict()
        orm = ORMTraining(**data)
        async with self._session_factory() as session:
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return training_from_orm(orm) if orm else None
    
    async def delete_training(self, id: UUID) -> None:
        async with self._session_factory() as session:
            orm = await session.get(ORMTraining, id)
            if not orm:
                return
            await session.delete(orm)
            await session.commit()
    
    async def update_training(self, training: DomainTraining) -> Optional[DomainTraining]:
        async with self._session_factory() as session:
            orm = await session.get(ORMTraining, training.id)
            if not orm:
                raise NotFoundError(f"Training {training.id} not found")
            for key, value in training.to_orm_dict().items():
                setattr(orm, key, value)
            await session.commit()
            return training_from_orm(orm) if orm else None
    
    async def find_all_owner_trainings(self, owner_id: UUID) -> Optional[List[DomainTraining]]:
        async with self._session_factory() as session:
            result = await session.execute(select(ORMTraining).filter(ORMTraining.owner_id == owner_id))
            orms = result.scalars().all()
            return [training_from_orm(orm) for orm in orms] if orms else []
    
    # CRUD Operation for Task
    async def add_task(self, task: DomainTask) -> Optional[DomainTask]:
        data = task.to_orm_dict()
        orm = ORMTask(**data)
        async with self._session_factory() as session:
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return task_from_orm(orm) if orm else None

    async def find_task_by_id(self, id: UUID) -> Optional[DomainTask]:
        async with self._session_factory() as session:
            # Utilisation de selectinload pour charger les validations en une seule requête
            result = await session.execute(
                select(ORMTask)
                .options(selectinload(ORMTask.validations))
                .filter(ORMTask.id == id)
            )
            orm = result.scalars().first()
            return task_from_orm(orm) if orm else None

    async def delete_task(self, id: UUID) -> None:
        async with self._session_factory() as session:
            orm = await session.get(ORMTask, id)
            if not orm:
                return
            await session.delete(orm)
            await session.commit()

    async def update_task(self, task: DomainTask) -> Optional[DomainTask]:
        async with self._session_factory() as session:
            orm = await session.get(ORMTask, task.id)
            if not orm:
                raise NotFoundError(f"Task {task.id} not found")
            for key, value in task.to_orm_dict().items():
                setattr(orm, key, value)
            await session.commit()
            return task_from_orm(orm) if orm else None
    
    async def find_tasks_by_training_id(self, training_id: UUID) -> Optional[List[DomainTask]]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ORMTask)
                .options(selectinload(ORMTask.validations))
                .filter(ORMTask.training_id == training_id)
            )
            orms = result.scalars().all()
            return [task_from_orm(orm) for orm in orms] if orms else []

    # validate methods
    async def add_validate(self, validate: DomainValidate) -> Optional[DomainValidate]:
        data = validate.to_orm_dict()
        orm = ORMValidate(**data)
        async with self._session_factory() as session:
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return validate_from_orm(orm) if orm else None

    async def find_validate_by_task_id(self, task_id: UUID) -> Optional[List[DomainValidate]]:
        async with self._session_factory() as session:
            result = await session.execute(select(ORMValidate).filter(ORMValidate.task_id == task_id))
            orms = result.scalars().all()
            return [validate_from_orm(orm) for orm in orms] if orms else None

    async def delete_validate(self, id: UUID) -> None:
        async with self._session_factory() as session:
            orm = await session.get(ORMValidate, id)
            if not orm:
                return
            await session.delete(orm)
            await session.commit()
    
    async def find_validate_by_id(self, id: UUID) -> Optional[DomainValidate]:
        async with self._session_factory() as session:
            orm = await session.get(ORMValidate, id)
            return validate_from_orm(orm) if orm else None
    
    async def find_all_validates_by_training_id(self, training_id: UUID) -> list[DomainValidate]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ORMValidate)
                .join(ORMTask, ORMValidate.task_id == ORMTask.id)
                .filter(ORMTask.training_id == training_id)
            )
            orms = result.scalars().all()
            return [validate_from_orm(v) for v in orms]