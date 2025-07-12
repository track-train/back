from typing import List, Optional
from sqlalchemy.orm import Session
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
    def __init__(self, session: Session):
        self._session = session

     # CRUD operations for Exercise
    def add(self, exercise: DomainExercise) -> Optional[DomainExercise]:
        data = exercise.to_orm_dict()
        orm = ORMExercise(**data)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return exercise_from_orm(orm) if orm else None
    
    def delete(self, id: UUID) -> None:
        orm = self._session.get(ORMExercise, id)
        if not orm:
            return
        self._session.delete(orm)
        self._session.commit()
    
    def update(self, exercise: DomainExercise) -> Optional[DomainExercise]:
        orm = self._session.get(ORMExercise, exercise.id)
        if not orm:
            raise NotFoundError(f"Exercise {exercise.id} not found")
        for key, value in exercise.to_orm_dict().items():
            setattr(orm, key, value)
        self._session.commit()
        return exercise_from_orm(orm) if orm else None
    
    def find_all_owner(self, owner_id: UUID) -> Optional[List[DomainExercise]]:
        orms = self._session.query(ORMExercise).filter(ORMExercise.owner_id == owner_id).all()
        return [exercise_from_orm(orm) for orm in orms] if orms else []
    
    def find_all(self) -> Optional[List[DomainExercise]]:
        orms = self._session.query(ORMExercise).all()
        return [exercise_from_orm(orm) for orm in orms] if orms else []
    
    def find_by_id(self, id: UUID) -> Optional[DomainExercise]:
        orm = self._session.get(ORMExercise, id)
        return exercise_from_orm(orm) if orm else None