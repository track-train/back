from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from src.domain.model.diet import Diet as DomainDiet, MacroPlan as DomainMacroPlan, MealPlan as DomainMealPlan

class DietRepository(ABC):
    @abstractmethod
    async def add_diet(self, diet: DomainDiet) -> DomainDiet:
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[DomainDiet]:
        pass

    @abstractmethod
    async def find_all_owner_diets(self, owner_id: UUID) -> List[DomainDiet]:
        pass

    @abstractmethod
    async def update_diet(self, diet: DomainDiet) -> DomainDiet:
        pass

    @abstractmethod
    async def delete_diet(self, id: UUID) -> None:
        pass


    @abstractmethod
    async def add_macro_plan(self, macro_plan: DomainMacroPlan) -> DomainMacroPlan:
        pass
    
    @abstractmethod
    async def find_macro_plan_by_id(self, id: UUID) -> Optional[DomainMacroPlan]:
        pass

    @abstractmethod
    async def find_macro_plans_by_user_id(self, user_id: UUID) -> List[DomainMacroPlan]:
        pass

    @abstractmethod
    async def delete_macro_plan(self, id: UUID) -> None:
        pass

    @abstractmethod
    async def find_macro_plans_by_diet_id(self, diet_id: UUID) -> List[DomainMacroPlan]:
        pass

    @abstractmethod
    async def update_macro_plan(self, macro_plan: DomainMacroPlan) -> DomainMacroPlan:
        pass


    @abstractmethod
    async def add_meal_plan(self, meal_plan: DomainMealPlan) -> DomainMealPlan:
        pass    

    @abstractmethod
    async def find_meal_plan_by_id(self, id: UUID) -> Optional[DomainMealPlan]:
        pass
    
    @abstractmethod
    async def find_meal_plans_by_user_id(self, user_id: UUID) -> List[DomainMealPlan]:
        pass

    @abstractmethod
    async def find_meal_plans_by_diet_id(self, diet_id: UUID) -> List[DomainMealPlan]:
        pass

    @abstractmethod
    async def update_meal_plan(self, meal_plan: DomainMealPlan) -> DomainMealPlan:
        pass

    @abstractmethod
    async def delete_meal_plan(self, id: UUID) -> None:
        pass

    