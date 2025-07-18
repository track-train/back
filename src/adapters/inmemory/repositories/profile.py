from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional, List

from src.domain.model.profile import Profile as DomainProfile
from src.domain.ports.profile_repository import ProfileRepository


class InMemoryProfileRepository(ProfileRepository):
    def __init__(self, initial: list[DomainProfile] | None = None):
        self._data: dict[UUID, DomainProfile] = {}
        if initial:
            for profile in initial:
                self._data[profile.id] = profile

    def find_by_email(self, email: str) -> Optional[DomainProfile]:
        for profile in self._data.values():
            if profile.email == email:
                return profile
        return None

    def add(self, profile: DomainProfile) -> DomainProfile:
        new_id = uuid4()
        profile.id = new_id
        if not getattr(profile, "created_at", None):
            profile.created_at = datetime.utcnow()
        self._data[new_id] = profile
        return profile

    def find_by_id(self, id: UUID) -> Optional[DomainProfile]:
        return self._data.get(id)

    def delete(self, id: UUID) -> None:
        self._data.pop(id, None)

    def update(self, profile: DomainProfile) -> Optional[DomainProfile]:
        if profile.id in self._data:
            self._data[profile.id] = profile
            return profile
        return None

    def find_all_users(self) -> List[DomainProfile]:
        return [p for p in self._data.values() if "user" in (p.roles or [])]

    def find_all_coachs(self) -> List[DomainProfile]:
        return [p for p in self._data.values() if "coach" in (p.roles or [])]
