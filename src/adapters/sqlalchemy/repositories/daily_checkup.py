from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from src.domain.exceptions import NotFoundError
from src.adapters.sqlalchemy.models import DailyCheckup as ORMDailyCheckup
from src.domain.model.daily_checkup import DailyCheckup as DomainDailyCheckup
from src.domain.ports.daily_checkup_repository import DailyCheckupRepository


class SqlAlchemyDailyCheckupRepository(DailyCheckupRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, daily_checkup: DomainDailyCheckup) -> DomainDailyCheckup:
        """Ajoute un nouveau daily checkup"""
        orm_checkup = ORMDailyCheckup(
            id=daily_checkup.id,
            profile_id=daily_checkup.profile_id,
            sleepduration=daily_checkup.sleepduration,
            sleepquality=daily_checkup.sleepquality,
            weight=daily_checkup.weight,
            shape=daily_checkup.shape,
            soreness=daily_checkup.soreness,
            steps=daily_checkup.steps,
            digestion=daily_checkup.digestion,
            dayon=daily_checkup.dayon,
            picture=daily_checkup.picture,
            created_at=daily_checkup.created_at,
        )
        self._session.add(orm_checkup)
        await self._session.commit()
        await self._session.refresh(orm_checkup)
        return self._to_domain(orm_checkup)

    async def find_by_id(self, id: UUID) -> Optional[DomainDailyCheckup]:
        """Trouve un daily checkup par son ID"""
        stmt = select(ORMDailyCheckup).where(ORMDailyCheckup.id == id)
        result = await self._session.execute(stmt)
        orm_checkup = result.scalar_one_or_none()
        if orm_checkup:
            return self._to_domain(orm_checkup)
        return None

    async def find_by_profile_id(self, profile_id: UUID) -> List[DomainDailyCheckup]:
        """Trouve tous les daily checkups d'un profil"""
        stmt = select(ORMDailyCheckup).where(
            ORMDailyCheckup.profile_id == profile_id
        ).order_by(ORMDailyCheckup.created_at.desc())
        result = await self._session.execute(stmt)
        orm_checkups = result.scalars().all()
        return [self._to_domain(checkup) for checkup in orm_checkups]

    async def find_by_profile_id_and_date(self, profile_id: UUID, target_date: date) -> Optional[DomainDailyCheckup]:
        """Trouve un daily checkup par profil et date"""
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        stmt = select(ORMDailyCheckup).where(
            and_(
                ORMDailyCheckup.profile_id == profile_id,
                ORMDailyCheckup.created_at >= start_of_day,
                ORMDailyCheckup.created_at <= end_of_day
            )
        )
        result = await self._session.execute(stmt)
        orm_checkup = result.scalar_one_or_none()
        if orm_checkup:
            return self._to_domain(orm_checkup)
        return None

    async def update(self, daily_checkup: DomainDailyCheckup) -> DomainDailyCheckup:
        """Met à jour un daily checkup existant"""
        orm_checkup = await self._session.get(ORMDailyCheckup, daily_checkup.id)
        if not orm_checkup:
            raise NotFoundError(f"Daily checkup {daily_checkup.id} not found")
        
        orm_checkup.sleepduration = daily_checkup.sleepduration
        orm_checkup.sleepquality = daily_checkup.sleepquality
        orm_checkup.weight = daily_checkup.weight
        orm_checkup.shape = daily_checkup.shape
        orm_checkup.soreness = daily_checkup.soreness
        orm_checkup.steps = daily_checkup.steps
        orm_checkup.digestion = daily_checkup.digestion
        orm_checkup.dayon = daily_checkup.dayon
        orm_checkup.picture = daily_checkup.picture
        
        await self._session.commit()
        await self._session.refresh(orm_checkup)
        return self._to_domain(orm_checkup)

    async def delete(self, id: UUID) -> None:
        """Supprime un daily checkup"""
        orm_checkup = await self._session.get(ORMDailyCheckup, id)
        if orm_checkup:
            await self._session.delete(orm_checkup)
            await self._session.commit()

    def _to_domain(self, orm_checkup: ORMDailyCheckup) -> DomainDailyCheckup:
        """Convertit un modèle ORM en modèle de domaine"""
        return DomainDailyCheckup(
            id=orm_checkup.id,
            profile_id=orm_checkup.profile_id,
            sleepduration=orm_checkup.sleepduration,
            sleepquality=orm_checkup.sleepquality,
            weight=orm_checkup.weight,
            shape=orm_checkup.shape,
            soreness=orm_checkup.soreness,
            steps=orm_checkup.steps,
            digestion=orm_checkup.digestion,
            dayon=orm_checkup.dayon,
            picture=orm_checkup.picture or [],
            created_at=orm_checkup.created_at,
        )