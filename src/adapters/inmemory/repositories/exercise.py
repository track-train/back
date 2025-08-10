from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime

from src.domain.model.exercise import Exercise as DomainExercise
from src.domain.ports.exercise_repository import ExerciseRepository
from src.domain.exceptions import NotFoundError

class InMemoryExerciseRepository(ExerciseRepository):
    def __init__(self):
        self._exercises: dict[UUID, DomainExercise] = {}

    async def add(self, exercise: DomainExercise) -> DomainExercise:
        new_id = uuid4()
        exercise.id = new_id
        if not getattr(exercise, 'created_at', None):
            exercise.created_at = datetime.utcnow()
        self._exercises[new_id] = exercise
        return exercise

    async def delete(self, id: UUID) -> None:
        self._exercises.pop(id, None)

    async def update(self, exercise: DomainExercise) -> Optional[DomainExercise]:
        if exercise.id not in self._exercises:
            raise NotFoundError(f"Exercise {exercise.id} not found")
        self._exercises[exercise.id] = exercise
        return exercise

    async def find_all_owner(self, owner_id: UUID) -> List[DomainExercise]:
        return [ex for ex in self._exercises.values() if ex.owner_id == owner_id]

    async def find_all(self) -> List[DomainExercise]:
        return list(self._exercises.values())

    async def find_by_id(self, id: UUID) -> Optional[DomainExercise]:
        return self._exercises.get(id)