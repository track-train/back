from typing import Optional, List
from uuid import UUID
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from src.domain.model.daily_checkup import DailyCheckup
from src.domain.ports.daily_checkup_repository import DailyCheckupRepository
from src.infrastructure.adapters.sql.models.daily_checkup_model import DailyCheckupModel

class SqlDailyCheckupRepository(DailyCheckupRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, daily_checkup: DailyCheckup) -> DailyCheckup:
        """Ajoute un nouveau daily checkup en base"""
        db_daily_checkup = DailyCheckupModel(
            id=daily_checkup.id,
            profile_id=daily_checkup.profile_id,
            date=daily_checkup.date,
            sleepduration=daily_checkup.sleepduration,
            sleepquality=daily_checkup.sleepquality,
            weight=daily_checkup.weight,
            shape=daily_checkup.shape,
            soreness=daily_checkup.soreness,
            steps=daily_checkup.steps,
            digestion=daily_checkup.digestion,
            dayon=daily_checkup.dayon,
            picture=json.dumps(daily_checkup.picture) if daily_checkup.picture else None,
            created_at=daily_checkup.created_at,
            updated_at=daily_checkup.updated_at
        )
        self._session.add(db_daily_checkup)
        await self._session.commit()
        await self._session.refresh(db_daily_checkup)
        return self._to_domain(db_daily_checkup)

    async def find_by_id(self, id: UUID) -> Optional[DailyCheckup]:
        """Trouve un daily checkup par son ID"""
        result = await self._session.execute(
            select(DailyCheckupModel).where(DailyCheckupModel.id == id)
        )
        db_daily_checkup = result.scalar_one_or_none()
        if db_daily_checkup is None:
            return None
        return self._to_domain(db_daily_checkup)

    async def find_by_profile_id(self, profile_id: UUID) -> List[DailyCheckup]:
        """Trouve tous les daily checkups d'un profil"""
        result = await self._session.execute(
            select(DailyCheckupModel)
            .where(DailyCheckupModel.profile_id == profile_id)
            .order_by(DailyCheckupModel.date.desc())
        )
        db_daily_checkups = result.scalars().all()
        return [self._to_domain(db_daily_checkup) for db_daily_checkup in db_daily_checkups]

    async def find_by_profile_id_and_date(self, profile_id: UUID, date: str) -> Optional[DailyCheckup]:
        """Trouve un daily checkup par profil et date"""
        result = await self._session.execute(
            select(DailyCheckupModel).where(
                and_(
                    DailyCheckupModel.profile_id == profile_id,
                    DailyCheckupModel.date == date
                )
            )
        )
        db_daily_checkup = result.scalar_one_or_none()
        if db_daily_checkup is None:
            return None
        return self._to_domain(db_daily_checkup)

    async def delete(self, id: UUID) -> None:
        """Supprime un daily checkup"""
        result = await self._session.execute(
            select(DailyCheckupModel).where(DailyCheckupModel.id == id)
        )
        db_daily_checkup = result.scalar_one_or_none()
        if db_daily_checkup is None:
            raise ValueError(f"Daily checkup with id {id} not found")
        await self._session.delete(db_daily_checkup)
        await self._session.commit()

    def _to_domain(self, db_daily_checkup: DailyCheckupModel) -> DailyCheckup:
        """Convertit un modèle DB en objet domain"""
        picture_list = []
        if db_daily_checkup.picture:
            try:
                picture_list = json.loads(db_daily_checkup.picture)
            except json.JSONDecodeError:
                picture_list = []
        return DailyCheckup(
            id=db_daily_checkup.id,
            profile_id=db_daily_checkup.profile_id,
            date=db_daily_checkup.date,
            sleepduration=db_daily_checkup.sleepduration,
            sleepquality=db_daily_checkup.sleepquality,
            weight=db_daily_checkup.weight,
            shape=db_daily_checkup.shape,
            soreness=db_daily_checkup.soreness,
            steps=db_daily_checkup.steps,
            digestion=db_daily_checkup.digestion,
            dayon=db_daily_checkup.dayon,
            picture=picture_list,
            created_at=db_daily_checkup.created_at,
            updated_at=db_daily_checkup.updated_at
        )