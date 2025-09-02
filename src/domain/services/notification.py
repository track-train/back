from uuid import UUID, uuid4
from datetime import datetime
from typing import List

from src.domain.model.notification import Notification as DomainNotification
from src.domain.ports.notification_repository import NotificationRepository
from src.domain.exceptions import NotFoundError

class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self._repo = repo

    async def get_unread_notifications(self, profile_id: UUID) -> List[DomainNotification]:
        return await self._repo.find_unread_by_profile_id(profile_id)

    async def mark_notification_as_read(self, notification_id: UUID, profile_id: UUID) -> DomainNotification:
        notification = await self._repo.find_by_id(notification_id)
        if not notification:
            raise NotFoundError(f"Notification with id {notification_id} not found")
        
        if notification.profile_id != profile_id:
            raise NotFoundError(f"Notification with id {notification_id} not found")
        
        if not notification.is_read():
            notification.mark_as_read()
            notification = await self._repo.update_notification(notification)
        
        return notification

    async def create_daily_notifications_for_all_users(self) -> List[DomainNotification]:
        profile_ids = await self._repo.find_all_profile_ids()
        
        notifications = []
        for profile_id in profile_ids:
            notification = DomainNotification(
                id=uuid4(),
                profile_id=profile_id,
                title="Daily Checkup",
                description="votre checkup journalié a remplir vous attends, ne faite pas attendre votre coach donner lui votre ressentie quautidien ;)",
                created_at=datetime.utcnow(),
                read_at=None
            )
            created_notification = await self._repo.add_notification(notification)
            notifications.append(created_notification)
        
        return notifications