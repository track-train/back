from typing import List, Optional
from uuid import UUID

from src.domain.model.notification import Notification as DomainNotification
from src.domain.ports.notification_repository import NotificationRepository

class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self, initial: List[DomainNotification] = None):
        self.notifications = initial or []

    async def add_notification(self, notification: DomainNotification) -> DomainNotification:
        self.notifications.append(notification)
        return notification

    async def find_by_id(self, id: UUID) -> Optional[DomainNotification]:
        for notification in self.notifications:
            if notification.id == id:
                return notification
        return None

    async def find_unread_by_profile_id(self, profile_id: UUID) -> List[DomainNotification]:
        unread_notifications = []
        for notification in self.notifications:
            if notification.profile_id == profile_id and not notification.is_read():
                unread_notifications.append(notification)
        
        unread_notifications.sort(key=lambda x: x.created_at, reverse=True)
        return unread_notifications

    async def update_notification(self, notification: DomainNotification) -> DomainNotification:
        for i, existing_notification in enumerate(self.notifications):
            if existing_notification.id == notification.id:
                self.notifications[i] = notification
                return notification
        return notification

    async def find_all_profile_ids(self) -> List[UUID]:
        profile_ids = set()
        for notification in self.notifications:
            profile_ids.add(notification.profile_id)
        return list(profile_ids)