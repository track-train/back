import os

from src.adapters.sqlalchemy.db import SessionLocal
from src.adapters.sqlalchemy.repositories.profile import SqlAlchemyProfileRepository
from src.adapters.sqlalchemy.repositories.group import SqlAlchemyGroupRepository
from src.adapters.sqlalchemy.repositories.training import SqlAlchemyTrainingRepository
from src.adapters.sqlalchemy.repositories.exercise import SqlAlchemyExerciseRepository
from src.adapters.sqlalchemy.repositories.diet import SqlAlchemyDietRepository


from src.domain.lib.security import BcryptPasswordHasher
from src.domain.services.group import GroupService
from src.domain.services.profile import ProfileService
from src.domain.services.training import TrainingService
from src.domain.services.exercise import ExerciseService 
from src.domain.services.diet import DietService

class Container:
    def __init__(self, env: str | None = None):
        self.env = os.getenv("ENV", "dev")
        self.hasher = BcryptPasswordHasher()

        self.SessionFactory = SessionLocal
    
    def get_profile_service(self):
        if self.env == "dev":
            # repo = InMemoryProfileRepository()
            pass
        else:
            session= self.SessionFactory()
            repo = SqlAlchemyProfileRepository(session)
        return ProfileService(repo, self.hasher)
        
    
    def get_group_service(self):
        if self.env == "dev":
            # repo = InMemoryGroupRepository()
            pass
        else:
            session = self.SessionFactory()
            repo = SqlAlchemyGroupRepository(session)
        return GroupService(repo)

    def get_training_service(self):
        if self.env == "dev":
            # repo = InMemoryTrainingRepository()
            pass
        else:
            session = self.SessionFactory()
            repo = SqlAlchemyTrainingRepository(session)
        return TrainingService(repo)
    
    def get_exercise_service(self):
        if self.env == "dev":
            # repo = InMemoryExerciseRepository()
            pass
        else:
            session = self.SessionFactory()
            repo = SqlAlchemyExerciseRepository(session)
        return ExerciseService(repo)

    def get_diet_service(self):
        if self.env == "dev":
            # repo = InMemoryDietRepository()
            pass
        else:
            session = self.SessionFactory()
            repo = SqlAlchemyDietRepository(session)
        return DietService(repo)



container = Container()