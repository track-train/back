from uuid import UUID, uuid4
from datetime import datetime
from typing import List
from src.domain.model.diet import Diet as DomainDiet, MacroPlan as DomainMacroPlan
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
    
    # Macro Plan methods

    def create_macro_plan(
        self,
        diet_id: UUID,
        name: str,
        carbohydrates: float,
        lipids: float,
        protein: float,
        fiber: float,
        water: float,
        kilocalorie: float
    ) -> DomainMacroPlan:
        if not name:
            raise ValueError("Name is required")
        plan = DomainMacroPlan(
            id=uuid4(),
            diet_id=diet_id,
            name=name,
            carbohydrates=carbohydrates,
            lipids=lipids,
            protein=protein,
            fiber=fiber,
            water=water,
            kilocalorie=kilocalorie,
        )
        return self._repo.add_macro_plan(plan)

    def get_macro_plans_for_diet(self, diet_id: UUID) -> List[DomainMacroPlan]:
        return self._repo.find_macro_plans_by_diet_id(diet_id)
    
    def get_macro_plans_by_user_id(self, user_id: UUID) -> List[DomainMacroPlan]:
        return self._repo.find_macro_plans_by_user_id(user_id)

    def get_macro_plan(self, plan_id: UUID) -> DomainMacroPlan:
        plan = self._repo.find_macro_plan_by_id(plan_id)
        if not plan:
            raise NotFoundError(f"MacroPlan {plan_id} not found")
        return plan

    def update_macro_plan(
        self,
        plan_id: UUID,
        name: str | None = None,
        carbohydrates: float | None = None,
        lipids: float | None = None,
        protein: float | None = None,
        fiber: float | None = None,
        water: float | None = None,
        kilocalorie: float | None = None,
    ) -> DomainMacroPlan:
        plan = self.get_macro_plan(plan_id)
        if name is not None:
            plan.name = name
        if carbohydrates is not None:
            plan.carbohydrates = carbohydrates
        if lipids is not None:
            plan.lipids = lipids
        if protein is not None:
            plan.protein = protein
        if fiber is not None:
            plan.fiber = fiber
        if water is not None:
            plan.water = water
        if kilocalorie is not None:
            plan.kilocalorie = kilocalorie
        return self._repo.update_macro_plan(plan)

    def delete_macro_plan(self, plan_id: UUID) -> None:
        # service lève NotFoundError si inexistant
        self.get_macro_plan(plan_id)
        self._repo.delete_macro_plan(plan_id)
