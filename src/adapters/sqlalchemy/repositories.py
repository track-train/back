from typing import Optional
from sqlalchemy.orm import Session
from src.domain.model.profile import Profile as DomainProfile
from src.adapters.sqlalchemy.models import Profile as ORMProfile
from src.domain.ports.profile_repository import ProfileRepository

class SqlAlchemyProfileRepository(ProfileRepository):
    def __init__(self, session: Session):
        self._session = session

    def find_by_email(self, email: str) -> Optional[DomainProfile]:
        orm = self._session.query(ORMProfile).filter(ORMProfile.email == email).one_or_none()
        return DomainProfile.from_orm(orm) if orm else None

    def add(self, profile: DomainProfile) -> DomainProfile:
        data = profile.to_orm_dict()
        orm = ORMProfile(**data)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return DomainProfile.from_orm(orm)