from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.exceptions import NotFoundError
from uuid import UUID

from src.adapters.sqlalchemy.models import Diet as ORMDiet, MealPlan as ORMMealPlan, MacroPlan as ORMMacroPlan
from src.domain.model.diet import Diet as DomainDiet, MealPlan as DomainMealPlan, MacroPlan as DomainMacroPlan
from src.domain.ports.diet_repository import DietRepository



def diet_from_orm(orm: ORMDiet) -> DomainDiet:
    return DomainDiet(
        id=orm.id,
        owner_id=orm.owner_id,
        name=orm.name,
        description=orm.description,
        created_at=orm.created_at,
    )

class SqlAlchemyDietRepository(DietRepository):
    def __init__(self, session: Session):
        self._session = session

    def add_diet(self, diet: DomainDiet) -> DomainDiet:
        data = diet.to_orm_dict()
        orm = ORMDiet(**data)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return diet_from_orm(orm)

    def find_by_id(self, id: UUID) -> Optional[DomainDiet]:
        orm = self._session.get(ORMDiet, id)
        return diet_from_orm(orm) if orm else None

    def find_all_owner_diets(self, owner_id: UUID) -> List[DomainDiet]:
        orms = (
            self._session
            .query(ORMDiet)
            .filter(ORMDiet.owner_id == owner_id)
            .all()
        )
        return [diet_from_orm(o) for o in orms]

    def update_diet(self, diet: DomainDiet) -> DomainDiet:
        orm = self._session.get(ORMDiet, diet.id)
        if not orm:
            raise NotFoundError(f"Diet {diet.id} not found")
        for k, v in diet.to_orm_dict().items():
            setattr(orm, k, v)
        self._session.commit()
        return diet_from_orm(orm)

    def delete_diet(self, id: UUID) -> None:
        orm = self._session.get(ORMDiet, id)
        if not orm:
            return
        self._session.delete(orm)
        self._session.commit()