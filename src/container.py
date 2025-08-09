import os
from uuid import uuid4, UUID
import asyncio

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
            return ProfileService(repo, self.hasher)
        else:
            from src.adapters.sqlalchemy.repositories.profile import SqlAlchemyProfileRepository
            
            class SessionManagedRepository:
                def __init__(self, repo_class, session_factory):
                    self.repo_class = repo_class
                    self.session_factory = session_factory
                
                def __getattr__(self, name):
                    async def method(*args, **kwargs):
                        async with self.session_factory() as session:
                            repo = self.repo_class(session)
                            repo_method = getattr(repo, name)
                            return await repo_method(*args, **kwargs)
                    return method
            
            repo = SessionManagedRepository(SqlAlchemyProfileRepository, self.SessionFactory)
            return ProfileService(repo, self.hasher)

    def get_group_service(self):
        if self.env in ("dev", "test"):
            repo = self.group_repo
            return GroupService(repo)
        else:
            from src.adapters.sqlalchemy.repositories.group import SqlAlchemyGroupRepository
            
            class SessionManagedRepository:
                def __init__(self, repo_class, session_factory):
                    self.repo_class = repo_class
                    self.session_factory = session_factory
                
                def __getattr__(self, name):
                    async def method(*args, **kwargs):
                        async with self.session_factory() as session:
                            repo = self.repo_class(session)
                            repo_method = getattr(repo, name)
                            return await repo_method(*args, **kwargs)
                    return method
            
            repo = SessionManagedRepository(SqlAlchemyGroupRepository, self.SessionFactory)
            return GroupService(repo)

    def get_training_service(self):
        if self.env in ("dev", "test"):
            repo = self.training_repo
            return TrainingService(repo)
        else:
            from src.adapters.sqlalchemy.repositories.training import SqlAlchemyTrainingRepository
            
            class SessionManagedRepository:
                def __init__(self, repo_class, session_factory):
                    self.repo_class = repo_class
                    self.session_factory = session_factory
                
                def __getattr__(self, name):
                    async def method(*args, **kwargs):
                        async with self.session_factory() as session:
                            repo = self.repo_class(session)
                            repo_method = getattr(repo, name)
                            return await repo_method(*args, **kwargs)
                    return method
            
            repo = SessionManagedRepository(SqlAlchemyTrainingRepository, self.SessionFactory)
            return TrainingService(repo)

    def get_exercise_service(self):
        if self.env in ("dev", "test"):
            repo = self.exercise_repo
            return ExerciseService(repo)
        else:
            from src.adapters.sqlalchemy.repositories.exercise import SqlAlchemyExerciseRepository
            
            class SessionManagedRepository:
                def __init__(self, repo_class, session_factory):
                    self.repo_class = repo_class
                    self.session_factory = session_factory
                
                def __getattr__(self, name):
                    async def method(*args, **kwargs):
                        async with self.session_factory() as session:
                            repo = self.repo_class(session)
                            repo_method = getattr(repo, name)
                            return await repo_method(*args, **kwargs)
                    return method
            
            repo = SessionManagedRepository(SqlAlchemyExerciseRepository, self.SessionFactory)
            return ExerciseService(repo)

    def get_diet_service(self):
        if self.env in ("dev", "test"):
            repo = self.diet_repo
            return DietService(repo)
        else:
            from src.adapters.sqlalchemy.repositories.diet import SqlAlchemyDietRepository
            
            class SessionManagedRepository:
                def __init__(self, repo_class, session_factory):
                    self.repo_class = repo_class
                    self.session_factory = session_factory
                
                def __getattr__(self, name):
                    async def method(*args, **kwargs):
                        async with self.session_factory() as session:
                            repo = self.repo_class(session)
                            repo_method = getattr(repo, name)
                            return await repo_method(*args, **kwargs)
                    return method
            
            repo = SessionManagedRepository(SqlAlchemyDietRepository, self.SessionFactory)
            return DietService(repo)

container = Container()
