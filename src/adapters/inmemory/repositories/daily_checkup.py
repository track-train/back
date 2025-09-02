from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, date

from src.domain.model.daily_checkup import DailyCheckup as DomainDailyCheckup
from src.domain.ports.daily_checkup_repository import DailyCheckupRepository
from src.domain.exceptions import NotFoundError

class InMemoryDailyCheckupRepository(DailyCheckupRepository):
    def __init__(self):
        self._daily_checkups: dict[UUID, DomainDailyCheckup] = {}

    async def add(self, daily_checkup: DomainDailyCheckup) -> DomainDailyCheckup:
        """Ajoute un nouveau daily checkup"""
        if not getattr(daily_checkup, "id", None):
            daily_checkup.id = uuid4()
        if not getattr(daily_checkup, "created_at", None):
            daily_checkup.created_at = datetime.utcnow()
        today = daily_checkup.created_at.date()
        existing = await self.find_by_profile_id_and_date(daily_checkup.profile_id, today)
        if existing:
            raise ValueError(f"Daily checkup already exists for profile {daily_checkup.profile_id} on {today}")
        self._daily_checkups[daily_checkup.id] = daily_checkup
        return daily_checkup

    async def find_by_id(self, id: UUID) -> Optional[DomainDailyCheckup]:
        """Trouve un daily checkup par son ID"""
        return self._daily_checkups.get(id)

    async def find_by_profile_id(self, profile_id: UUID) -> List[DomainDailyCheckup]:
        """Trouve tous les daily checkups d'un profil, triés du plus récent au plus ancien"""
        checkups = [dc for dc in self._daily_checkups.values() if dc.profile_id == profile_id]
        return sorted(checkups, key=lambda x: x.created_at, reverse=True)

    async def find_by_profile_id_and_date(self, profile_id: UUID, target_date: date) -> Optional[DomainDailyCheckup]:
        """Trouve un daily checkup par profil et date (même jour)"""
        for checkup in self._daily_checkups.values():
            if (
                checkup.profile_id == profile_id
                and checkup.created_at.date() == target_date
            ):
                return checkup
        return None

    async def delete(self, id: UUID) -> None:
        """Supprime un daily checkup"""
        self._daily_checkups.pop(id, None)