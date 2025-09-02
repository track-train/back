from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

@dataclass
class Notification:
    id: UUID = field(default_factory=uuid4)
    profile_id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None

    def to_orm_dict(self) -> dict:
        return {
            "id": str(self.id),
            "profile_id": str(self.profile_id),
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "read_at": self.read_at,
        }
    
    def is_read(self) -> bool:
        return self.read_at is not None
    
    def mark_as_read(self) -> None:
        if self.read_at is None:
            self.read_at = datetime.utcnow()