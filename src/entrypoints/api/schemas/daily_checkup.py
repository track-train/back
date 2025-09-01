from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class DailyCheckupCreate(BaseModel):
    sleepduration: Optional[str] = Field(None, description="Durée de sommeil")
    sleepquality: Optional[int] = Field(None, ge=1, le=10, description="Qualité du sommeil (1-10)")
    weight: Optional[float] = Field(None, gt=0, description="Poids en kg")
    shape: Optional[int] = Field(None, ge=1, le=10, description="Forme physique (1-10)")
    soreness: Optional[int] = Field(None, ge=1, le=10, description="Courbatures (1-10)")
    steps: Optional[int] = Field(None, ge=0, description="Nombre de pas")
    digestion: Optional[int] = Field(None, ge=1, le=10, description="Digestion (1-10)")
    dayon: Optional[bool] = Field(None, description="Jour on/off")

class DailyCheckupResponse(BaseModel):
    id: UUID
    profile_id: UUID
    date: str
    sleepduration: Optional[str]
    sleepquality: Optional[int]
    weight: Optional[float]
    shape: Optional[int]
    soreness: Optional[int]
    steps: Optional[int]
    digestion: Optional[int]
    dayon: Optional[bool]
    picture: List[str] = Field(default_factory=list, description="URLs des images")
    created_at: datetime

    class Config:
        from_attributes = True

class DailyCheckupListResponse(BaseModel):
    daily_checkups: List[DailyCheckupResponse]
    total: int

class MessageResponse(BaseModel):
    message: str