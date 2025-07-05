from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class ProfileCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[int] = None
    contact: Optional[str] = None
    pricing: Optional[float] = None
    description: Optional[str] = None
    legacy: Optional[str] = None

class ProfileRead(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str] = None
    sex: Optional[str]
    age: Optional[int]
    contact: Optional[str]
    pricing: Optional[float]
    description: Optional[str]
    legacy: Optional[str]
    roles: List[str]
    created_at: datetime

    class Config:
        orm_mode = True