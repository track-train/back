import os
from src.adapters.sqlalchemy.repositories.profile import SqlAlchemyProfileRepository
from src.adapters.sqlalchemy.repositories.group import SqlAlchemyGroupRepository
from src.adapters.sqlalchemy.db import SessionLocal
from src.domain.lib.security import BcryptPasswordHasher
from src.domain.services.group import GroupService
from src.domain.services.profile import ProfileService

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




container = Container()