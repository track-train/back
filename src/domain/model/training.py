from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

@dataclass
class Validate:
    id: UUID = field(default_factory=uuid4)
    task_id: UUID = field(default_factory=uuid4)
    exercise_name: str = ""
    updated_at: datetime = field(default_factory=datetime.utcnow)
    rest_time: Optional[int] = None
    repetitions: Optional[int] = None
    set_number: Optional[int] = None
    rir: Optional[int] = None
    succeeded_at: Optional[datetime] = None

    def to_orm_dict(self) -> dict:
        return {
            "id": str(self.id),
            "task_id": str(self.task_id),
            "rest_time": self.rest_time,
            "repetitions": self.repetitions,
            "set_number": self.set_number,
            "rir": self.rir,
            "updated_at": self.updated_at,
            "succeeded_at": self.succeeded_at if self.succeeded_at else None,
        }

@dataclass
class Task:
    id: UUID = field(default_factory=uuid4)
    training_id: UUID = field(default_factory=uuid4)
    exercise_name: str = ""
    rest_time: Optional[int] = None
    repetitions: Optional[int] = None
    set_number: Optional[int] = None
    method: Optional[str] = None
    rir: Optional[int] = None
    validate: List [Validate] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_orm_dict(self) -> dict:
        return {
            "id": str(self.id),
            "training_id": str(self.training_id),
            "rest_time": self.rest_time,
            "exercise_name": self.exercise_name,
            "repetitions": self.repetitions,
            "set_number": self.set_number,
            "method": self.method,
            "rir": self.rir,
            "updated_at": self.updated_at,
            "validate": [v.to_orm_dict() for v in self.validate] if self.validate else None,
        }

@dataclass
class Training:
    id: UUID = field(default_factory=uuid4)
    owner_id: UUID = field(default_factory=uuid4)
    name: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    description: Optional[str] = None
    tasks: List[Task] = field(default_factory=list)

    def to_orm_dict(self) -> dict:
        return {
            "id": str(self.id),
            "owner_id": str(self.owner_id),
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "tasks": [task.to_orm_dict() for task in self.tasks],
        }