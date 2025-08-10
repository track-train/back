from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

@dataclass
class Group:
    id: UUID = field(default_factory=uuid4)
    owner_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_orm_dict(self) -> dict:
        return {
            "id": str(self.id),
            "owner_id": str(self.owner_id),
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at
        }