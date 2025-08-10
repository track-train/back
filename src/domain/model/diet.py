from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

@dataclass
class Diet:
    id: UUID = field(default_factory=uuid4)
    owner_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    name: str = ""
    description: Optional[str] = None

    def to_orm_dict(self) -> dict:
        return {
            "id": str(self.id),
            "created_at": self.created_at,
            "owner_id": str(self.owner_id),
            "name": self.name,
            "description": self.description,
        }
    
@dataclass
class MacroPlan:
    id: UUID = field(default_factory=uuid4)
    diet_id: UUID = field(default_factory=uuid4)
    name: str = ""
    carbohydrates: Optional[float] = None
    lipids: Optional[float] = None
    protein: Optional[float] = None
    fiber: Optional[float] = None
    water: Optional[float] = None
    kilocalorie: Optional[float] = None

    def to_orm_dict(self) -> dict:
        return {
            "id": str(self.id),
            "diet_id": str(self.diet_id),
            "name": self.name,
            "carbohydrates": self.carbohydrates,
            "lipids": self.lipids,
            "protein": self.protein,
            "fiber": self.fiber,
            "water": self.water,
            "kilocalorie": self.kilocalorie,
        }

@dataclass
class MealItem:
    timing: str
    food: str

@dataclass
class MealPlan:
    id: UUID = field(default_factory=uuid4)
    diet_id: UUID = field(default_factory=uuid4)
    name: str = ""
    meals: List[MealItem] = field(default_factory=list)

    def to_orm_dict(self) -> dict:
        return {
            "id": str(self.id),
            "diet_id": str(self.diet_id),
            "name": self.name,
            "meals": [meal.__dict__ for meal in self.meals],
        }



