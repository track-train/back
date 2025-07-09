from abc import ABC, abstractmethod
from src.domain.model.profile import Profile
from typing import Optional
from uuid import UUID

class ProfileRepository(ABC):
    @abstractmethod
    def add(self, profile: Profile) -> Profile:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Profile]:
        pass

    @abstractmethod
    def delete(self, id: UUID) -> None:
        pass

    @abstractmethod
    def find_by_id(self, id: UUID)  -> Optional[Profile]:
        pass

    @abstractmethod
    def update(self, profile: Profile) -> Profile:
        pass