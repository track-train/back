from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from src.domain.model.notification import Notification as DomainNotification
from src.domain.ports.notification_repository import NotificationRepository
from src.adapters.sqlalchemy.models import Notification as SqlAlchemyNotification, Profile as SqlAlchemyProfile

class SqlAlchemyNotificationRepository(NotificationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_notification(self, notification: DomainNotification) -> DomainNotification:
        orm_notification = SqlAlchemyNotification(**notification.to_orm_dict())
        self.session.add(orm_notification)
        await self.session.commit()
        await self.session.refresh(orm_notification)
        
        return DomainNotification(
            id=orm_notification.id,
            profile_id=orm_notification.profile_id,
            title=orm_notification.title,
            description=orm_notification.description,
            created_at=orm_notification.created_at,
            read_at=orm_notification.read_at
        )

    async def find_by_id(self, id: UUID) -> Optional[DomainNotification]:
        result = await self.session.execute(
            select(SqlAlchemyNotification).where(SqlAlchemyNotification.id == id)
        )
        orm_notification = result.scalar_one_or_none()
        
        if not orm_notification:
            return None
        
        return DomainNotification(
            id=orm_notification.id,
            profile_id=orm_notification.profile_id,
            title=orm_notification.title,
            description=orm_notification.description,
            created_at=orm_notification.created_at,
            read_at=orm_notification.read_at
        )

    async def find_unread_by_profile_id(self, profile_id: UUID) -> List[DomainNotification]:
        result = await self.session.execute(
            select(SqlAlchemyNotification)
            .where(SqlAlchemyNotification.profile_id == profile_id)
            .where(SqlAlchemyNotification.read_at.is_(None))
            .order_by(SqlAlchemyNotification.created_at.desc())
        )
        orm_notifications = result.scalars().all()
        
        return [
            DomainNotification(
                id=orm_notification.id,
                profile_id=orm_notification.profile_id,
                title=orm_notification.title,
                description=orm_notification.description,
                created_at=orm_notification.created_at,
                read_at=orm_notification.read_at
            )
            for orm_notification in orm_notifications
        ]

    async def update_notification(self, notification: DomainNotification) -> DomainNotification:
        result = await self.session.execute(
            select(SqlAlchemyNotification).where(SqlAlchemyNotification.id == notification.id)
        )
        orm_notification = result.scalar_one_or_none()
        
        if orm_notification:
            orm_notification.title = notification.title
            orm_notification.description = notification.description
            orm_notification.read_at = notification.read_at
            
            await self.session.commit()
            await self.session.refresh(orm_notification)
        
        return notification

    async def find_all_profile_ids(self) -> List[UUID]:
        result = await self.session.execute(
            select(SqlAlchemyProfile.id)
        )
        profile_ids = result.scalars().all()
        return list(profile_ids)