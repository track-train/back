from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from src.entrypoints.api.schemas.notification import NotificationRead, DailyNotificationResponse
from src.entrypoints.api.deps.roles import get_current_user, require_roles
from src.domain.exceptions import NotFoundError
from src.container import container

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/mine", response_model=List[NotificationRead])
async def get_my_unread_notifications(
    user: dict = Depends(get_current_user)
):
    try:
        current_user_id = UUID(user["sub"])
        notification_service = container.get_notification_service()
        notifications = await notification_service.get_unread_notifications(current_user_id)
        if not notifications:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No unread notifications found"
            )
        return notifications
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error when fetching notifications: {str(e)}"
        )

@router.patch("/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_as_read(
    notification_id: UUID,
    user: dict = Depends(get_current_user)
):
    try:
        current_user_id = UUID(user["sub"])
        notification_service = container.get_notification_service()
        notification = await notification_service.mark_notification_as_read(
            notification_id, current_user_id
        )
        return notification
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error when updating notification: {str(e)}"
        )

@router.post("/create-daily", response_model=DailyNotificationResponse, dependencies=[Depends(require_roles("admin"))])
async def create_daily_notifications():
    try:
        notification_service = container.get_notification_service()
        notifications = await notification_service.create_daily_notifications_for_all_users()
        
        return DailyNotificationResponse(
            message="Daily notifications created successfully",
            notifications_created=len(notifications)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error when creating daily notifications: {str(e)}"
        )