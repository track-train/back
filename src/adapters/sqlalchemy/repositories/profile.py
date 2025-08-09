from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from uuid import UUID

from src.domain.model.profile import Profile as DomainProfile
from src.domain.ports.profile_repository import ProfileRepository
from src.adapters.sqlalchemy.models.profile import Profile as SQLProfile

class SQLAlchemyProfileRepository(ProfileRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def find_by_email(self, email: str) -> Optional[DomainProfile]:
        async with self._session_factory() as session:  # ✅ Correct usage
            stmt = select(SQLProfile).where(SQLProfile.email == email)
            result = await session.execute(stmt)
            sql_profile = result.scalar_one_or_none()
            
            if sql_profile:
                return sql_profile.to_domain()
            return None

    async def add(self, profile: DomainProfile) -> DomainProfile:
        async with self._session_factory() as session:
            sql_profile = SQLProfile.from_domain(profile)
            session.add(sql_profile)
            await session.commit()
            await session.refresh(sql_profile)
            return sql_profile.to_domain()

    async def find_by_id(self, id: UUID) -> Optional[DomainProfile]:
        async with self._session_factory() as session:
            stmt = select(SQLProfile).where(SQLProfile.id == id)
            result = await session.execute(stmt)
            sql_profile = result.scalar_one_or_none()
            
            if sql_profile:
                return sql_profile.to_domain()
            return None

    async def delete(self, id: UUID) -> None:
        async with self._session_factory() as session:
            stmt = select(SQLProfile).where(SQLProfile.id == id)
            result = await session.execute(stmt)
            sql_profile = result.scalar_one_or_none()
            
            if sql_profile:
                await session.delete(sql_profile)
                await session.commit()

    async def update(self, profile: DomainProfile) -> Optional[DomainProfile]:
        async with self._session_factory() as session:
            stmt = select(SQLProfile).where(SQLProfile.id == profile.id)
            result = await session.execute(stmt)
            sql_profile = result.scalar_one_or_none()
            
            if sql_profile:
                # Mettre à jour les champs
                sql_profile.email = profile.email
                sql_profile.password = profile.password
                sql_profile.name = profile.name
                sql_profile.sex = profile.sex
                sql_profile.age = profile.age
                sql_profile.contact = profile.contact
                sql_profile.pricing = profile.pricing
                sql_profile.description = profile.description
                sql_profile.legacy = profile.legacy
                sql_profile.roles = profile.roles
                
                await session.commit()
                await session.refresh(sql_profile)
                return sql_profile.to_domain()
            return None

    async def find_all_users(self) -> List[DomainProfile]:
        async with self._session_factory() as session:
            stmt = select(SQLProfile).where(SQLProfile.roles.contains(["user"]))
            result = await session.execute(stmt)
            sql_profiles = result.scalars().all()
            return [profile.to_domain() for profile in sql_profiles]

    async def find_all_coachs(self) -> List[DomainProfile]:
        async with self._session_factory() as session:
            stmt = select(SQLProfile).where(SQLProfile.roles.contains(["coach"]))
            result = await session.execute(stmt)
            sql_profiles = result.scalars().all()
            return [profile.to_domain() for profile in sql_profiles]