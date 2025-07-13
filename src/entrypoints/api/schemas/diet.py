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
