from abc import ABC, abstractmethod
from src.domain.model.profile import Profile
from typing import Optional

class ProfileRepository(ABC):
    @abstractmethod
    def add(self, profile: Profile) -> Profile:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Profile]:
        pass