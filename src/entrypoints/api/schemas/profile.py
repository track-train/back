from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class ProfileCreate(BaseModel):
    email: str
    password: str
    confirm_password: str
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
    profile_picture_url: Optional[str] = None
    background_picture_url: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class CoachProfileRead(BaseModel):
    id: UUID
    name: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[int] = None
    contact: Optional[str] = None
    pricing: Optional[float] = None
    description: Optional[str] = None
    legacy: Optional[str] = None
    profile_picture_url: Optional[str] = None
    background_picture_url: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class ProfileWithToken(BaseModel):
    profile: ProfileRead
    token: TokenResponse

class ProfileLogin(BaseModel):
    email: str
    password: str

class ProfilUpdate(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str]          = None
    sex: Optional[str]           = None
    age: Optional[int]           = None
    contact: Optional[str]       = None
    pricing: Optional[float]     = None
    description: Optional[str]   = None
    legacy: Optional[str]        = None

class EmailUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr

class PasswordUpdate(BaseModel):
    old_password: str = Field(..., alias="oldPassword")
    new_password: str = Field(..., alias="newPassword")

class RolesUpdate(BaseModel):
    roles: List[str]