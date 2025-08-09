from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.domain.exceptions import NotFoundError
from uuid import UUID

from src.adapters.sqlalchemy.models import Exercise as ORMExercise
from src.domain.model.exercise import Exercise as DomainExercise
from src.domain.ports.exercise_repository import ExerciseRepository



def exercise_from_orm(orm_exercise) -> DomainExercise:
    return DomainExercise(
        id=orm_exercise.id,
        name=orm_exercise.name,
        owner_id=orm_exercise.owner_id,
        description=orm_exercise.description,
        created_at=orm_exercise.created_at,
    )

class SqlAlchemyExerciseRepository(ExerciseRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

     # CRUD operations for Exercise
    async def add(self, exercise: DomainExercise) -> Optional[DomainExercise]:
        data = exercise.to_orm_dict()
        orm = ORMExercise(**data)
        async with self._session_factory() as session:
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return exercise_from_orm(orm) if orm else None
    
    async def delete(self, id: UUID) -> None:
        async with self._session_factory() as session:
            orm = await session.get(ORMExercise, id)
            if not orm:
                return
            await session.delete(orm)
            await session.commit()
    
    async def update(self, exercise: DomainExercise) -> Optional[DomainExercise]:
        async with self._session_factory() as session:
            orm = await session.get(ORMExercise, exercise.id)
            if not orm:
                raise NotFoundError(f"Exercise {exercise.id} not found")
            for key, value in exercise.to_orm_dict().items():
                setattr(orm, key, value)
            await session.commit()
            return exercise_from_orm(orm) if orm else None
    
    async def find_all_owner(self, owner_id: UUID) -> Optional[List[DomainExercise]]:
        async with self._session_factory() as session:
            result = await session.execute(select(ORMExercise).filter(ORMExercise.owner_id == owner_id))
            orms = result.scalars().all()
            return [exercise_from_orm(orm) for orm in orms] if orms else []
    
    async def find_all(self) -> Optional[List[DomainExercise]]:
        async with self._session_factory() as session:
            result = await session.execute(select(ORMExercise))
            orms = result.scalars().all()
            return [exercise_from_orm(orm) for orm in orms] if orms else []
    
    async def find_by_id(self, id: UUID) -> Optional[DomainExercise]:
        async with self._session_factory() as session:
            orm = await session.get(ORMExercise, id)
            return exercise_from_orm(orm) if orm else None