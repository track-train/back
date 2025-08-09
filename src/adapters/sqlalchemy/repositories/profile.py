from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_email(self, email: str) -> Optional[DomainProfile]:
        stmt = select(ORMProfile).where(ORMProfile.email == email)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return profil_from_orm(orm) if orm else None

    async def add(self, profile: DomainProfile) -> Optional[DomainProfile]:
        data = profile.to_orm_dict()
        orm = ORMProfile(**data)
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return profil_from_orm(orm) if orm else None
    
    async def find_by_id(self, id: UUID) -> Optional[DomainProfile]:
        # SQLAlchemy 1.4+ : session.get
        orm = await self._session.get(ORMProfile, id)
        return profil_from_orm(orm) if orm else None
    
    async def delete(self, id: UUID) -> None:
        orm = await self._session.get(ORMProfile, id)
        if not orm:
            return
        await self._session.delete(orm)
        await self._session.commit()
    
    async def update(self, profile: DomainProfile) -> Optional[DomainProfile]:
        orm = await self._session.get(ORMProfile, profile.id)
        if not orm:
            return None
        for key, value in profile.to_orm_dict().items():
            setattr(orm, key, value)
        await self._session.commit()
        await self._session.refresh(orm)
        return profil_from_orm(orm) 
    
    async def find_all_users(self)-> list[DomainProfile]:
        stmt = select(ORMProfile).where(ORMProfile.roles.any('user'))
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [profil_from_orm(orm) for orm in orms] if orms else []
    
    async def find_all_coachs(self)-> list[DomainProfile]:
        stmt = select(ORMProfile).where(ORMProfile.roles.any('coach'))
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [profil_from_orm(orm) for orm in orms] if orms else []