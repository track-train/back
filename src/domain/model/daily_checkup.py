from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from typing import List, Optional

@dataclass
class DailyCheckup:
    profile_id: UUID
    id: Optional[UUID] = None
    sleepduration: Optional[str] = None
    sleepquality: Optional[int] = None
    weight: Optional[float] = None
    shape: Optional[int] = None
    soreness: Optional[int] = None
    steps: Optional[int] = None
    digestion: Optional[int] = None
    dayon: Optional[bool] = None
    picture: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def _validate_score_fields(self):
        score_fields = {
            'sleepquality': self.sleepquality,
            'shape': self.shape, 
            'soreness': self.soreness,
            'digestion': self.digestion
        }
        
        for field_name, value in score_fields.items():
            if value is not None and not (1 <= value <= 10):
                raise ValueError(f"{field_name} must be between 1 and 10")

    def to_orm_dict(self) -> dict:
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'sleepduration': self.sleepduration,
            'sleepquality': self.sleepquality,
            'weight': self.weight,
            'shape': self.shape,
            'soreness': self.soreness,
            'steps': self.steps,
            'digestion': self.digestion,
            'dayon': self.dayon,
            'picture': self.picture,
            'created_at': self.created_at,
        }