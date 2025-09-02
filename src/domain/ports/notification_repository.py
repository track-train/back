from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from src.domain.model.notification import Notification as DomainNotification

class NotificationRepository(ABC):
    @abstractmethod
    async def add_notification(self, notification: DomainNotification) -> DomainNotification:
        pass

    @abstractmethod
    async def find_by_id(self, id: UUID) -> Optional[DomainNotification]:
        pass

    @abstractmethod
    async def find_unread_by_profile_id(self, profile_id: UUID) -> List[DomainNotification]:
        pass

    @abstractmethod
    async def update_notification(self, notification: DomainNotification) -> DomainNotification:
        pass

    @abstractmethod
    async def find_all_profile_ids(self) -> List[UUID]:
        pass