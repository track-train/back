from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ExerciseCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ExerciseRead(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config= {
        "from_attributes": True
    }

class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None