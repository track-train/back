from contextlib import asynccontextmanager
from typing import AsyncGenerator
from src.adapters.sqlalchemy.db import SessionLocal
from src.adapters.sqlalchemy.repositories.diet import SqlAlchemyDietRepository
from src.adapters.sqlalchemy.repositories.profile import SqlAlchemyProfileRepository
from src.adapters.sqlalchemy.repositories.group import SqlAlchemyGroupRepository
from src.adapters.sqlalchemy.repositories.exercise import SqlAlchemyExerciseRepository
from src.adapters.sqlalchemy.repositories.training import SqlAlchemyTrainingRepository
from src.domain.services.diet import DietService
from src.domain.services.profile import ProfileService
from src.domain.services.group import GroupService
from src.domain.services.exercise import ExerciseService
from src.domain.services.training import TrainingService
from src.domain.lib.security import BcryptPasswordHasher
from src.container import container
import os


async def get_async_session():
    """Dependency to get async database session."""
    async with SessionLocal() as session:
        yield session


async def get_diet_service():
    """Dependency to get diet service with async session."""
    if container.env in ("dev", "test"):
        yield container.get_diet_service()
    else:
        async with SessionLocal() as session:
            repo = SqlAlchemyDietRepository(session)
            yield DietService(repo)


async def get_profile_service():
    """Dependency to get profile service with async session."""
    if container.env in ("dev", "test"):
        yield container.get_profile_service()
    else:
        async with SessionLocal() as session:
            repo = SqlAlchemyProfileRepository(session)
            hasher = BcryptPasswordHasher()
            yield ProfileService(repo, hasher)


async def get_group_service():
    """Dependency to get group service with async session."""
    if container.env in ("dev", "test"):
        yield container.get_group_service()
    else:
        async with SessionLocal() as session:
            repo = SqlAlchemyGroupRepository(session)
            yield GroupService(repo)


async def get_exercise_service():
    """Dependency to get exercise service with async session."""
    if container.env in ("dev", "test"):
        yield container.get_exercise_service()
    else:
        async with SessionLocal() as session:
            repo = SqlAlchemyExerciseRepository(session)
            yield ExerciseService(repo)


async def get_training_service():
    """Dependency to get training service with async session."""
    if container.env in ("dev", "test"):
        yield container.get_training_service()
    else:
        async with SessionLocal() as session:
            repo = SqlAlchemyTrainingRepository(session)
            yield TrainingService(repo)