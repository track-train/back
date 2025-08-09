from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.domain.exceptions import NotFoundError
from uuid import UUID

from src.adapters.sqlalchemy.models import Diet as ORMDiet, MealPlan as ORMMealPlan, MacroPlan as ORMMacroPlan
from src.domain.model.diet import Diet as DomainDiet, MealPlan as DomainMealPlan, MacroPlan as DomainMacroPlan, MealItem as DomainMealItem
from src.domain.ports.diet_repository import DietRepository

def diet_from_orm(orm: ORMDiet) -> DomainDiet:
    return DomainDiet(
        id=orm.id,
        owner_id=orm.owner_id,
        name=orm.name,
        description=orm.description,
        created_at=orm.created_at,
    )

def macro_plan_from_orm(orm: ORMMacroPlan) -> DomainMacroPlan:
    return DomainMacroPlan(
        id=orm.id,
        diet_id=orm.diet_id,
        name=orm.name,
        carbohydrates=orm.carbohydrates,
        lipids=orm.lipids,
        protein=orm.protein,
        fiber=orm.fiber,
        water=orm.water,
        kilocalorie=orm.kilocalorie,
    )

def meal_plan_from_orm(orm: ORMMealPlan) -> DomainMealPlan:
    domain_meals: List[DomainMealItem] = [
        DomainMealItem(**meal_dict) for meal_dict in (orm.meals or [])
    ]
    return DomainMealPlan(
        id=orm.id,
        diet_id=orm.diet_id,
        name=orm.name,
        meals=domain_meals,
    )

class SqlAlchemyDietRepository(DietRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def add_diet(self, diet: DomainDiet) -> DomainDiet:
        data = diet.to_orm_dict()
        orm = ORMDiet(**data)
        async with self._session_factory() as session:
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return diet_from_orm(orm)

    async def find_by_id(self, id: UUID) -> Optional[DomainDiet]:
        async with self._session_factory() as session:
            orm = await session.get(ORMDiet, id)
            return diet_from_orm(orm) if orm else None

    async def find_all_owner_diets(self, owner_id: UUID) -> List[DomainDiet]:
        async with self._session_factory() as session:
            result = await session.execute(select(ORMDiet).filter(ORMDiet.owner_id == owner_id))
            orms = result.scalars().all()
            return [diet_from_orm(o) for o in orms]

    async def update_diet(self, diet: DomainDiet) -> DomainDiet:
        async with self._session_factory() as session:
            orm = await session.get(ORMDiet, diet.id)
            if not orm:
                raise NotFoundError(f"Diet {diet.id} not found")
            for k, v in diet.to_orm_dict().items():
                setattr(orm, k, v)
            await session.commit()
            return diet_from_orm(orm)

    async def delete_diet(self, id: UUID) -> None:
        async with self._session_factory() as session:
            orm = await session.get(ORMDiet, id)
            if not orm:
                return
            await session.delete(orm)
            await session.commit()
        
# Macro Plan methods

    async def add_macro_plan(self, macro_plan: DomainMacroPlan) -> DomainMacroPlan:
        data = macro_plan.to_orm_dict()
        orm = ORMMacroPlan(**data)
        async with self._session_factory() as session:
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return macro_plan_from_orm(orm)

    async def find_macro_plan_by_id(self, id: UUID) -> Optional[DomainMacroPlan]:
        async with self._session_factory() as session:
            orm = await session.get(ORMMacroPlan, id)
            return macro_plan_from_orm(orm) if orm else None

    async def find_macro_plans_by_diet_id(self, diet_id: UUID) -> List[DomainMacroPlan]:
        async with self._session_factory() as session:
            result = await session.execute(select(ORMMacroPlan).filter(ORMMacroPlan.diet_id == diet_id))
            orms = result.scalars().all()
            return [macro_plan_from_orm(o) for o in orms]
    
    async def find_macro_plans_by_user_id(self, user_id: UUID) -> List[DomainMacroPlan]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ORMMacroPlan)
                .join(ORMDiet, ORMDiet.id == ORMMacroPlan.diet_id)
                .filter(ORMDiet.owner_id == user_id)
            )
            orms = result.scalars().all()
            return [macro_plan_from_orm(o) for o in orms]

    async def update_macro_plan(self, macro_plan: DomainMacroPlan) -> DomainMacroPlan:
        async with self._session_factory() as session:
            orm = await session.get(ORMMacroPlan, macro_plan.id)
            if not orm:
                raise NotFoundError(f"MacroPlan {macro_plan.id} not found")
            for k, v in macro_plan.to_orm_dict().items():
                setattr(orm, k, v)
            await session.commit()
            return macro_plan_from_orm(orm)

    async def delete_macro_plan(self, id: UUID) -> None:
        async with self._session_factory() as session:
            orm = await session.get(ORMMacroPlan, id)
            if not orm:
                return
            await session.delete(orm)
            await session.commit()

# Meal Plan methods

    async def add_meal_plan(self, mp: DomainMealPlan) -> DomainMealPlan:
        data = mp.to_orm_dict()
        orm = ORMMealPlan(**data)
        async with self._session_factory() as session:
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return meal_plan_from_orm(orm)

    async def find_meal_plan_by_id(self, id: UUID) -> Optional[DomainMealPlan]:
        async with self._session_factory() as session:
            orm = await session.get(ORMMealPlan, id)
            return meal_plan_from_orm(orm) if orm else None

    async def find_meal_plans_by_diet_id(self, diet_id: UUID) -> List[DomainMealPlan]:
        async with self._session_factory() as session:
            result = await session.execute(select(ORMMealPlan).filter(ORMMealPlan.diet_id == diet_id))
            orms = result.scalars().all()
            return [meal_plan_from_orm(o) for o in orms]

    async def find_meal_plans_by_user_id(self, user_id: UUID) -> List[DomainMealPlan]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ORMMealPlan)
                .join(ORMDiet)
                .filter(ORMDiet.owner_id == user_id)
            )
            orms = result.scalars().all()
            return [meal_plan_from_orm(o) for o in orms]

    async def update_meal_plan(self, mp: DomainMealPlan) -> DomainMealPlan:
        async with self._session_factory() as session:
            orm = await session.get(ORMMealPlan, mp.id)
            if not orm:
                raise NotFoundError(f"MealPlan {mp.id} not found")
            for k, v in mp.to_orm_dict().items():
                setattr(orm, k, v)
            await session.commit()
            return meal_plan_from_orm(orm)

    async def delete_meal_plan(self, id: UUID) -> None:
        async with self._session_factory() as session:
            orm = await session.get(ORMMealPlan, id)
            if orm:
                await session.delete(orm)
                await session.commit()