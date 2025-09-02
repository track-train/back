from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class DailyCheckupCreate(BaseModel):
    sleepduration: Optional[str] = None
    sleepquality: Optional[int] = Field(None, ge=1, le=10)
    weight: Optional[float] = Field(None, gt=0)
    shape: Optional[int] = Field(None, ge=1, le=10)
    soreness: Optional[int] = Field(None, ge=1, le=10)
    steps: Optional[int] = Field(None, ge=0)
    digestion: Optional[int] = Field(None, ge=1, le=10)
    dayon: Optional[bool] = None
class DailyCheckupRead(BaseModel):
    id: UUID
    profile_id: UUID
    sleepduration: Optional[str]
    sleepquality: Optional[int]
    weight: Optional[float]
    shape: Optional[int]
    soreness: Optional[int]
    steps: Optional[int]
    digestion: Optional[int]
    dayon: Optional[bool]
    picture: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}