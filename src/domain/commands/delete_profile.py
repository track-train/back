from pydantic import BaseModel
from uuid import UUID

class DeleteProfileCommand(BaseModel):
    id: UUID