from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class GroupRead(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GroupList(BaseModel):
    groups: List[GroupRead]

    model_config = ConfigDict(from_attributes=True)

class GroupMember(BaseModel):
    id: UUID
    name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)