import os
from uuid import uuid4, UUID

from src.domain.lib.security import BcryptPasswordHasher
from src.domain.services.profile import ProfileService
from src.domain.services.group import GroupService
from src.domain.services.training import TrainingService
from src.domain.services.exercise import ExerciseService
from src.domain.services.diet import DietService

class Container:
    def __init__(self, env: str | None = None):
        self.env = env if env is not None else os.getenv("ENV", "dev")
        self.hasher = BcryptPasswordHasher()

        if self.env in ("dev", "test"):
            from src.domain.model.profile import Profile as DomainProfile
            plain_pw = "123456789"
            hashed_pw = self.hasher.hash(plain_pw)
            admin = DomainProfile(
                id=uuid4(),
                email="admin@mail.fr",
                password=hashed_pw,
                name="Admin",
                sex=None,
                age=None,
                contact=None,
                pricing=None,
                description=None,
                legacy=False,
                roles=["admin"],
                created_at=None,
            )
            from src.adapters.inmemory.repositories.profile import InMemoryProfileRepository
            from src.adapters.inmemory.repositories.group import InMemoryGroupRepository
            from src.adapters.inmemory.repositories.training import InMemoryTrainingRepository
            from src.adapters.inmemory.repositories.exercise import InMemoryExerciseRepository
            from src.adapters.inmemory.repositories.diet import InMemoryDietRepository
            self.profile_repo = InMemoryProfileRepository(initial=[admin])
            self.group_repo = InMemoryGroupRepository(self.profile_repo)
            self.training_repo = InMemoryTrainingRepository()
            self.exercise_repo = InMemoryExerciseRepository()
            self.diet_repo = InMemoryDietRepository()
        else:
            from src.adapters.sqlalchemy.db import SessionLocal
            self.SessionFactory = SessionLocal

    def get_profile_service(self):
        if self.env in ("dev", "test"):
            repo = self.profile_repo
        else:
            from src.adapters.sqlalchemy.repositories.profile import SqlAlchemyProfileRepository
            session = self.SessionFactory()
            repo = SqlAlchemyProfileRepository(session)
        return ProfileService(repo, self.hasher)

    def get_group_service(self):
        if self.env in ("dev", "test"):
            repo = self.group_repo
        else:
            from src.adapters.sqlalchemy.repositories.group import SqlAlchemyGroupRepository
            session = self.SessionFactory()
            repo = SqlAlchemyGroupRepository(session)
        return GroupService(repo)

    def get_training_service(self):
        if self.env in ("dev", "test"):
            repo = self.training_repo
        else:
            from src.adapters.sqlalchemy.repositories.training import SqlAlchemyTrainingRepository
            session = self.SessionFactory()
            repo = SqlAlchemyTrainingRepository(session)
        return TrainingService(repo)

    def get_exercise_service(self):
        if self.env in ("dev", "test"):
            repo = self.exercise_repo
        else:
            from src.adapters.sqlalchemy.repositories.exercise import SqlAlchemyExerciseRepository
            session = self.SessionFactory()
            repo = SqlAlchemyExerciseRepository(session)
        return ExerciseService(repo)

    def get_diet_service(self):
        if self.env in ("dev", "test"):
            repo = self.diet_repo
        else:
            from src.adapters.sqlalchemy.repositories.diet import SqlAlchemyDietRepository
            session = self.SessionFactory()
            repo = SqlAlchemyDietRepository(session)
        return DietService(repo)

container = Container()
