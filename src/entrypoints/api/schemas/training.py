from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class TrainingCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TrainingRead(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class TrainingUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class TaskRead(BaseModel):
    id: UUID
    exercise_name: str
    rest_time: Optional[int]
    repetitions: Optional[int]
    set_number: Optional[int]
    method: Optional[str]
    rir: Optional[int]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    exercise_name: str
    rest_time: Optional[int] = None
    repetitions: Optional[int] = None
    set_number: Optional[int] = None
    method: Optional[str] = None
    rir: Optional[int] = None

class TaskUpdate(BaseModel):
    exercise_name: Optional[str] = None
    rest_time: Optional[int] = None
    repetitions: Optional[int] = None
    set_number: Optional[int] = None
    method: Optional[str] = None
    rir: Optional[int] = None


class ValidateRead(BaseModel):
    id: UUID
    task_id: UUID
    rest_time: Optional[int]
    repetitions: Optional[int]
    set_number: Optional[int]
    rir: Optional[int]
    updated_at: datetime
    succeeded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ValidateCreate(BaseModel):
    rest_time: Optional[int] = None
    repetitions: Optional[int] = None
    set_number: Optional[int] = None
    rir: Optional[int] = None

