from pydantic import BaseModel, EmailStr
from typing import List, Optional

class CreateProfileCommand(BaseModel):
    email: EmailStr
    password: str
    name: str
    sex: Optional[str] = None
    age: Optional[int] = None
    contact: Optional[str] = None
    pricing: Optional[float] = None
    description: Optional[str] = None
    legacy: Optional[str] = None
    roles: List[str] = []