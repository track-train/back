from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

Base = declarative_base()

# Many-to-many for group membership
group_users = Table(
    'group_users', Base.metadata,
    Column('group_id', UUID(as_uuid=True), ForeignKey('groups.id'), primary_key=True),
    Column('profile_id', UUID(as_uuid=True), ForeignKey('profiles.id'), primary_key=True)
)

class RequestType(enum.Enum):
    REQUEST = "REQUEST"
    INVITATION = "INVITATION"

class RequestStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DENIED = "DENIED"

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    sex = Column(String)
    age = Column(Integer)
    contact = Column(String)
    pricing = Column(Float)
    description = Column(String)
    legacy = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Roles stored as an array of role names
    roles = Column(ARRAY(String), nullable=False, default=lambda: ["user"])

    # Group relations: users who have accepted invitations
    groups = relationship("Group", secondary=group_users, back_populates="users")

    # Other relationships
    notifications = relationship("Notification", back_populates="profile")
    mensurations = relationship("Mensuration", back_populates="profile")
    weights = relationship("Weight", back_populates="profile")
    heights = relationship("Height", back_populates="profile")
    exercises = relationship("Exercise", back_populates="owner")
    trainings = relationship("Training", back_populates="owner")
    diets = relationship("Diet", back_populates="owner")
    requests_sent = relationship("Request", foreign_keys='Request.owner_id', back_populates="owner")
    requests_received = relationship("Request", foreign_keys='Request.target_id', back_populates="target")

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    permissions = Column(ARRAY(String), nullable=False, default=list)

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    created_at = Column(DateTime)
    read_at = Column(DateTime)
    title = Column(String)
    description = Column(String)

    profile = relationship("Profile", back_populates="notifications")

class Mensuration(Base):
    __tablename__ = 'mensurations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    created_at = Column(DateTime)
    forearms = Column(Float)
    chest = Column(Float)
    legs = Column(Float)
    neck = Column(Float)
    arms = Column(Float)
    shoulder = Column(Float)
    buttock = Column(Float)
    ankle = Column(Float)
    wrist = Column(Float)

    profile = relationship("Profile", back_populates="mensurations")

class Weight(Base):
    __tablename__ = 'weights'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    created_at = Column(DateTime)
    weight = Column(Float)

    profile = relationship("Profile", back_populates="weights")

class Height(Base):
    __tablename__ = 'heights'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'))
    created_at = Column(DateTime)
    height = Column(Float)

    profile = relationship("Profile", back_populates="heights")

class Exercise(Base):
    __tablename__ = 'exercises'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)

    owner = relationship("Profile", back_populates="exercises")
    tasks = relationship("Task", back_populates="exercise")

class Training(Base):
    __tablename__ = 'trainings'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)

    owner = relationship("Profile", back_populates="trainings")
    tasks = relationship("Task", back_populates="training")

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    training_id = Column(UUID(as_uuid=True), ForeignKey('trainings.id'), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey('exercises.id'), nullable=False)
    rest_time = Column(Integer)
    repetitions = Column(Integer)
    set_number = Column(Integer)
    method = Column(String)
    rir = Column(Integer)
    updated_at = Column(DateTime)
    validate = Column(String)

    training = relationship("Training", back_populates="tasks")
    exercise = relationship("Exercise", back_populates="tasks")
    validations = relationship("Validation", back_populates="task")

class Validation(Base):
    __tablename__ = 'validations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey('tasks.id'))
    rest_time = Column(Integer)
    repetitions = Column(Integer)
    set_number = Column(Integer)
    rir = Column(Integer)
    updated_at = Column(DateTime)
    succeeded_at = Column(DateTime)

    task = relationship("Task", back_populates="validations")

class Diet(Base):
    __tablename__ = 'diets'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)

    owner = relationship("Profile", back_populates="diets")
    macro_plans = relationship("MacroPlan", back_populates="diet")
    meal_plans = relationship("MealPlan", back_populates="diet")

class MacroPlan(Base):
    __tablename__ = 'macro_plans'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diet_id = Column(UUID(as_uuid=True), ForeignKey('diets.id'))
    name = Column(String, nullable=False)
    carbohydrates = Column(Float)
    lipids = Column(Float)
    protein = Column(Float)
    fiber = Column(Float)
    water = Column(Float)
    kilocalorie = Column(Float)

    diet = relationship("Diet", back_populates="macro_plans")

class MealPlan(Base):
    __tablename__ = 'meal_plans'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diet_id = Column(UUID(as_uuid=True), ForeignKey('diets.id'))
    name = Column(String, nullable=False)
    meals = Column(String)

    diet = relationship("Diet", back_populates="meal_plans")

class Request(Base):
    __tablename__ = 'requests'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey('groups.id'))
    type = Column(Enum(RequestType))
    title = Column(String)
    description = Column(String)
    sent_at = Column(DateTime)
    status = Column(Enum(RequestStatus))

    owner = relationship("Profile", foreign_keys=[owner_id], back_populates="requests_sent")
    target = relationship("Profile", foreign_keys=[target_id], back_populates="requests_received")
    group = relationship("Group", back_populates="requests")

class Group(Base):
    __tablename__ = 'groups'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float)
    place = Column(String)

    owner = relationship("Profile", backref="owned_groups")
    users = relationship("Profile", secondary=group_users, back_populates="groups")
    requests = relationship("Request", back_populates="group")
