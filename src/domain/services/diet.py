from uuid import UUID, uuid4
from datetime import datetime
from typing import List
from src.domain.model.diet import Diet as DomainDiet
from src.domain.ports.diet_repository import DietRepository
from src.domain.exceptions import NotFoundError

class DietService:
    def __init__(self, repo: DietRepository):
        self._repo = repo

    def create_diet(self, *, owner_id: UUID, name: str, description: str = "") -> DomainDiet:
        if not name:
            raise ValueError("Diet name cannot be empty")
        diet = DomainDiet(
            id=uuid4(),
            owner_id=owner_id,
            name=name,
            description=description,
            created_at=datetime.utcnow(),
        )
        return self._repo.add_diet(diet)

    def get_diet(self, diet_id: UUID) -> DomainDiet:
        diet = self._repo.find_by_id(diet_id)
        if not diet:
            raise NotFoundError(f"Diet {diet_id} not found")
        return diet

    def list_owner_diets(self, owner_id: UUID) -> List[DomainDiet]:
        return self._repo.find_all_owner_diets(owner_id)

    def update_diet(self, diet_id: UUID, name: str | None = None, description: str | None = None) -> DomainDiet:
        diet = self._repo.find_by_id(diet_id)
        if not diet:
            raise NotFoundError(f"Diet {diet_id} not found")
        if name is not None:
            diet.name = name
        if description is not None:
            diet.description = description
        return self._repo.update_diet(diet)

    def delete_diet(self, diet_id: UUID) -> None:
        if not self._repo.find_by_id(diet_id):
            raise NotFoundError(f"Diet {diet_id} not found")
        self._repo.delete_diet(diet_id)
