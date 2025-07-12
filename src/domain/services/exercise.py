from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

from src.domain.model.exercise import Exercise as DomainExercise
from src.domain.ports.exercise_repository import ExerciseRepository
from src.domain.exceptions import NotFoundError

class ExerciseService:
    def __init__(self, repo: ExerciseRepository):
        self._repo = repo

    def create_exercise(self, *,
                        owner_id: UUID,
                        name: str,
                        description: Optional[str] = None) -> DomainExercise:
        if not name:
            raise ValueError("Exercise name cannot be empty")

        exercise = DomainExercise(
            id=uuid4(),
            owner_id=owner_id,
            name=name,
            description=description,
            created_at=datetime.utcnow(),
        )

        return self._repo.add(exercise)

    def delete_exercise(self, exercise_id: UUID):
        self._repo.delete(exercise_id)

    def update_exercise(self,  
        exercise_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None
        ) -> DomainExercise:
        exercise = self._repo.find_by_id(exercise_id)
        if not exercise:
            raise NotFoundError(f"Exercise {exercise_id} not found")
        
        if name is not None:
            exercise.name = name
        if description is not None:
            exercise.description = description
        return self._repo.update(exercise)

    def get_exercises_mine(self, owner_id: UUID) -> List[DomainExercise]:
        exercises = self._repo.find_all_owner(owner_id)
        if not exercises:
            raise NotFoundError(f"No exercises found for owner {owner_id}")
        return exercises
    
    def get_all_exercises(self) -> List[DomainExercise]:
        exercises = self._repo.find_all()
        if not exercises:
            raise NotFoundError("No exercises found")
        return exercises
    