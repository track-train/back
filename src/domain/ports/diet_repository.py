from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from src.domain.model.diet import Diet as DomainDiet, MacroPlan as DomainMacroPlan, MealPlan as DomainMealPlan

class DietRepository(ABC):
    @abstractmethod
    def add_diet(self, diet: DomainDiet) -> DomainDiet:
        pass

    @abstractmethod
    def find_by_id(self, id: UUID) -> Optional[DomainDiet]:
        pass

    @abstractmethod
    def find_all_owner_diets(self, owner_id: UUID) -> List[DomainDiet]:
        pass

    @abstractmethod
    def update_diet(self, diet: DomainDiet) -> DomainDiet:
        pass

    @abstractmethod
    def delete_diet(self, id: UUID) -> None:
        pass

# Macro Plan methods

    @abstractmethod
    def add_macro_plan(self, macro_plan: DomainMacroPlan) -> DomainMacroPlan:
        pass
    
    @abstractmethod
    def find_macro_plan_by_id(self, id: UUID) -> Optional[DomainMacroPlan]:
        pass

    @abstractmethod
    def find_macro_plans_by_user_id(self, user_id: UUID) -> List[DomainMacroPlan]:
        pass

    @abstractmethod
    def delete_macro_plan(self, id: UUID) -> None:
        pass

    @abstractmethod
    def find_macro_plans_by_diet_id(self, diet_id: UUID) -> List[DomainMacroPlan]:
        pass

    @abstractmethod
    def update_macro_plan(self, macro_plan: DomainMacroPlan) -> DomainMacroPlan:
        pass

# Meal Plan methods

    @abstractmethod
    def add_meal_plan(self, meal_plan: DomainMealPlan) -> DomainMealPlan:
        pass    

    @abstractmethod
    def find_meal_plan_by_id(self, id: UUID) -> Optional[DomainMealPlan]:
        pass
    
    @abstractmethod
    def find_meal_plans_by_user_id(self, user_id: UUID) -> List[DomainMealPlan]:
        pass

    @abstractmethod
    def find_meal_plans_by_diet_id(self, diet_id: UUID) -> List[DomainMealPlan]:
        pass

    @abstractmethod
    def update_meal_plan(self, meal_plan: DomainMealPlan) -> DomainMealPlan:
        pass

    @abstractmethod
    def delete_meal_plan(self, id: UUID) -> None:
        pass

    