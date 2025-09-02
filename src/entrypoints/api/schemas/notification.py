from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class NotificationRead(BaseModel):
    id: UUID
    profile_id: UUID
    title: str
    description: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class NotificationUpdate(BaseModel):
    read_at: datetime

class DailyNotificationResponse(BaseModel):
    message: str
    notifications_created: int