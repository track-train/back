from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime


@dataclass
class Exercise:
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    owner_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    description: Optional[str] = None

    def to_orm_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "owner_id": str(self.owner_id),
            "description": self.description,
            "created_at": self.created_at,
        }