from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class DietCreate(BaseModel):
    name: str
    description: Optional[str] = None

class DietRead(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DietUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class MacroPlanCreate(BaseModel):
    name: str
    carbohydrates: float
    lipids: float
    protein: float
    fiber: float
    water: float
    kilocalorie: float

class MacroPlanRead(BaseModel):
    id: UUID
    diet_id: UUID
    name: str
    carbohydrates: float
    lipids: float
    protein: float
    fiber: float
    water: float
    kilocalorie: float

    model_config = ConfigDict(from_attributes=True)

class MacroPlanUpdate(BaseModel):
    name: Optional[str] = None
    carbohydrates: Optional[float] = None
    lipids: Optional[float] = None
    protein: Optional[float] = None
    fiber: Optional[float] = None
    water: Optional[float] = None
    kilocalorie: Optional[float] = None

class MealItemRead(BaseModel):
    timing: str
    food: str

    model_config = {"from_attributes": True}

class MealPlanCreate(BaseModel):
    name: str
    meals: List[MealItemRead]

class MealPlanRead(BaseModel):
    id: UUID
    diet_id: UUID
    name: str
    meals: List[MealItemRead]

    model_config = {"from_attributes": True}

class MealPlanUpdate(BaseModel):
    name: Optional[str] = None
    meals: Optional[List[MealItemRead]] = None