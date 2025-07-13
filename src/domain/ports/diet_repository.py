from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from src.domain.model.diet import Diet as DomainDiet

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
