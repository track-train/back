from typing import Optional
from sqlalchemy.orm import Session
from src.domain.model.profile import Profile as DomainProfile
from src.adapters.sqlalchemy.models import Profile as ORMProfile
from src.domain.ports.profile_repository import ProfileRepository
from uuid import UUID   

def profil_from_orm(orm_profile) ->DomainProfile:
    return DomainProfile(
        id=orm_profile.id,
        email=orm_profile.email,
        password=orm_profile.password,
        name=orm_profile.name,
        sex=orm_profile.sex,
        age=orm_profile.age,
        contact=orm_profile.contact,
        pricing=orm_profile.pricing,
        description=orm_profile.description,
        legacy=orm_profile.legacy,
        roles=orm_profile.roles,
        created_at=orm_profile.created_at,
    )



class SqlAlchemyProfileRepository(ProfileRepository):
    def __init__(self, session: Session):
        self._session = session

    def find_by_email(self, email: str) -> Optional[DomainProfile]:
        orm = self._session.query(ORMProfile).filter(ORMProfile.email == email).one_or_none()
        return profil_from_orm(orm) if orm else None

    def add(self, profile: DomainProfile) -> Optional[DomainProfile]:
        data = profile.to_orm_dict()
        orm = ORMProfile(**data)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return profil_from_orm(orm) if orm else None
    
    def find_by_id(self, id: UUID) -> Optional[DomainProfile]:
        # SQLAlchemy 1.4+ : session.get
        orm = self._session.get(ORMProfile, id)
        return profil_from_orm(orm) if orm else None
    
    def delete(self, id: UUID) -> None:
        orm = self._session.get(ORMProfile, id)
        if not orm:
            return
        self._session.delete(orm)
        self._session.commit()