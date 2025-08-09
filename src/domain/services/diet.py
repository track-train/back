from uuid import UUID, uuid4
from datetime import datetime
from typing import List
from src.domain.model.diet import Diet as DomainDiet, MacroPlan as DomainMacroPlan, MealPlan as DomainMealPlan, MealItem as DomainMealItem
from src.domain.ports.diet_repository import DietRepository
from src.domain.exceptions import NotFoundError

class DietService:
    def __init__(self, repo: DietRepository):
        self._repo = repo

    async def create_diet(self, *, owner_id: UUID, name: str, description: str = "") -> DomainDiet:
        if not name:
            raise ValueError("Diet name cannot be empty")
        diet = DomainDiet(
            id=uuid4(),
            owner_id=owner_id,
            name=name,
            description=description,
            created_at=datetime.utcnow(),
        )
        return await self._repo.add_diet(diet)

    async def get_diet(self, diet_id: UUID) -> DomainDiet:
        diet = await self._repo.find_by_id(diet_id)
        if not diet:
            raise NotFoundError(f"Diet {diet_id} not found")
        return diet

    async def list_owner_diets(self, owner_id: UUID) -> List[DomainDiet]:
        return await self._repo.find_all_owner_diets(owner_id)

    async def update_diet(self, diet_id: UUID, name: str | None = None, description: str | None = None) -> DomainDiet:
        diet = await self._repo.find_by_id(diet_id)
        if not diet:
            raise NotFoundError(f"Diet {diet_id} not found")
        if name is not None:
            diet.name = name
        if description is not None:
            diet.description = description
        return await self._repo.update_diet(diet)

    async def delete_diet(self, diet_id: UUID) -> None:
        if not await self._repo.find_by_id(diet_id):
            raise NotFoundError(f"Diet {diet_id} not found")
        await self._repo.delete_diet(diet_id)
    
    # Macro Plan methods

    async def create_macro_plan(
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
        return await self._repo.add_macro_plan(plan)

    async def get_macro_plans_for_diet(self, diet_id: UUID) -> List[DomainMacroPlan]:
        return await self._repo.find_macro_plans_by_diet_id(diet_id)
    
    async def get_macro_plans_by_user_id(self, user_id: UUID) -> List[DomainMacroPlan]:
        return await self._repo.find_macro_plans_by_user_id(user_id)

    async def get_macro_plan(self, plan_id: UUID) -> DomainMacroPlan:
        plan = await self._repo.find_macro_plan_by_id(plan_id)
        if not plan:
            raise NotFoundError(f"MacroPlan {plan_id} not found")
        return plan

    async def update_macro_plan(
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
        plan = await self.get_macro_plan(plan_id)
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
        return await self._repo.update_macro_plan(plan)

    async def delete_macro_plan(self, plan_id: UUID) -> None:
        await self.get_macro_plan(plan_id)
        await self._repo.delete_macro_plan(plan_id)
    
    # Meal Plan methods

    async def create_meal_plan(
        self,
        diet_id: UUID,
        name: str,
        meals: list[dict],
    ) -> DomainMealPlan:
        
        domain_meals = [DomainMealItem(**m.model_dump()) for m in meals]
        if not name:
            raise ValueError("Meal Plan name cannot be empty")
        
        mp = DomainMealPlan(
            id=uuid4(),
            diet_id=diet_id,
            name=name,
            meals=domain_meals,
        )
        return await self._repo.add_meal_plan(mp)

    async def get_meal_plan_by_id(self, id: UUID) -> DomainMealPlan:
        mp = await self._repo.find_meal_plan_by_id(id)
        if not mp:
            raise NotFoundError(f"MealPlan {id} not found")
        return mp

    async def get_meal_plans_by_diet(self, diet_id: UUID) -> list[DomainMealPlan]:
        return await self._repo.find_meal_plans_by_diet_id(diet_id)

    async def get_meal_plans_by_user(self, user_id: UUID) -> list[DomainMealPlan]:
        return await self._repo.find_meal_plans_by_user_id(user_id)

    async def update_meal_plan(
        self,
        plan_id: UUID,
        name: str | None = None,
        meals: list[dict] | None = None,
    ) -> DomainMealPlan:
        mp = await self.get_meal_plan_by_id(plan_id)

        updated_name = name if name is not None else mp.name
        updated_meals = [DomainMealItem(**m.model_dump()) for m in meals] if meals is not None else mp.meals

        if not updated_meals:
            raise ValueError("Meal Plan must have at least one meal")
        
        if name is not None:
            mp.name = updated_name
        if meals is not None:
            mp.meals = updated_meals
        return await self._repo.update_meal_plan(mp)

    async def delete_meal_plan(self, plan_id: UUID) -> None:
        await self.get_meal_plan_by_id(plan_id)
        await self._repo.delete_meal_plan(plan_id)

