from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime

from src.domain.model.diet import Diet as DomainDiet, MacroPlan as DomainMacroPlan, MealPlan as DomainMealPlan, MealItem as DomainMealItem
from src.domain.ports.diet_repository import DietRepository
from src.domain.exceptions import NotFoundError

class InMemoryDietRepository(DietRepository):
    def __init__(self):
        self._diets: dict[UUID, DomainDiet] = {}
        self._macro_plans: dict[UUID, DomainMacroPlan] = {}
        self._meal_plans: dict[UUID, DomainMealPlan] = {}

    # Diet methods
    async def add_diet(self, diet: DomainDiet) -> DomainDiet:
        new_id = uuid4()
        diet.id = new_id
        if not getattr(diet, 'created_at', None):
            diet.created_at = datetime.utcnow()
        self._diets[new_id] = diet
        return diet

    async def find_by_id(self, id: UUID) -> Optional[DomainDiet]:
        return self._diets.get(id)

    async def find_all_owner_diets(self, owner_id: UUID) -> List[DomainDiet]:
        return [d for d in self._diets.values() if d.owner_id == owner_id]

    async def update_diet(self, diet: DomainDiet) -> DomainDiet:
        if diet.id not in self._diets:
            raise NotFoundError(f"Diet {diet.id} not found")
        self._diets[diet.id] = diet
        return diet

    async def delete_diet(self, id: UUID) -> None:
        self._diets.pop(id, None)
        for mid in list(self._macro_plans.keys()):
            if self._macro_plans[mid].diet_id == id:
                self.delete_macro_plan(mid)
        for pid in list(self._meal_plans.keys()):
            if self._meal_plans[pid].diet_id == id:
                self.delete_meal_plan(pid)

    # MacroPlan methods
    async def add_macro_plan(self, macro_plan: DomainMacroPlan) -> DomainMacroPlan:
        new_id = uuid4()
        macro_plan.id = new_id
        self._macro_plans[new_id] = macro_plan
        return macro_plan

    async def find_macro_plan_by_id(self, id: UUID) -> Optional[DomainMacroPlan]:
        return self._macro_plans.get(id)

    async def find_macro_plans_by_diet_id(self, diet_id: UUID) -> List[DomainMacroPlan]:
        return [mp for mp in self._macro_plans.values() if mp.diet_id == diet_id]

    async def find_macro_plans_by_user_id(self, user_id: UUID) -> List[DomainMacroPlan]:
        return [mp for mp in self._macro_plans.values() if self._diets.get(mp.diet_id) and self._diets[mp.diet_id].owner_id == user_id]

    async def update_macro_plan(self, macro_plan: DomainMacroPlan) -> DomainMacroPlan:
        if macro_plan.id not in self._macro_plans:
            raise NotFoundError(f"MacroPlan {macro_plan.id} not found")
        self._macro_plans[macro_plan.id] = macro_plan
        return macro_plan

    async def delete_macro_plan(self, id: UUID) -> None:
        self._macro_plans.pop(id, None)

    # MealPlan methods
    async def add_meal_plan(self, meal_plan: DomainMealPlan) -> DomainMealPlan:
        new_id = uuid4()
        meal_plan.id = new_id
        self._meal_plans[new_id] = meal_plan
        return meal_plan

    async def find_meal_plan_by_id(self, id: UUID) -> Optional[DomainMealPlan]:
        return self._meal_plans.get(id)

    async def find_meal_plans_by_diet_id(self, diet_id: UUID) -> List[DomainMealPlan]:
        return [mp for mp in self._meal_plans.values() if mp.diet_id == diet_id]

    async def find_meal_plans_by_user_id(self, user_id: UUID) -> List[DomainMealPlan]:
        return [mp for mp in self._meal_plans.values() if self._diets.get(mp.diet_id) and self._diets[mp.diet_id].owner_id == user_id]

    async def update_meal_plan(self, meal_plan: DomainMealPlan) -> DomainMealPlan:
        if meal_plan.id not in self._meal_plans:
            raise NotFoundError(f"MealPlan {meal_plan.id} not found")
        self._meal_plans[meal_plan.id] = meal_plan
        return meal_plan

    async def delete_meal_plan(self, id: UUID) -> None:
        self._meal_plans.pop(id, None)
