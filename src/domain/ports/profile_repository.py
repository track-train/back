from abc import ABC, abstractmethod
from src.domain.model.profile import Profile
from typing import Optional
from uuid import UUID

class ProfileRepository(ABC):
    @abstractmethod
    async def add(self, profile: Profile) -> Profile:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Profile]:
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID)  -> Optional[Profile]:
        pass

    @abstractmethod
    async def update(self, profile: Profile) -> Profile:
        pass

    @abstractmethod
    async def find_all_users(self) -> list[Profile]:
        pass
    
    @abstractmethod
    async def find_all_coachs(self) -> list[Profile]:
        pass