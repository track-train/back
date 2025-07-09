from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from typing import List, Optional

@dataclass
class Profile:
    id: UUID
    email: str
    password: str
    name: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[int] = None
    contact: Optional[str] = None
    pricing: Optional[float] = None
    description: Optional[str] = None
    legacy: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


    def to_orm_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "sex": self.sex,
            "age": self.age,
            "contact": self.contact,
            "pricing": self.pricing,
            "description": self.description,
            "legacy": self.legacy,
            "roles": self.roles,
            "created_at": self.created_at,
        }