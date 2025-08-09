from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.domain.exceptions import NotFoundError
from src.domain.model.group import Group as DomainGroup
from src.domain.model.profile import Profile as DomainProfile
from src.adapters.sqlalchemy.models import Group as ORMGroup, group_users, Profile as ORMProfile
from src.domain.ports.group_repository import GroupRepository
from src.adapters.sqlalchemy.repositories.profile import profil_from_orm
from uuid import UUID   

def group_from_orm(orm_group) -> DomainGroup:
    return DomainGroup(
        id=orm_group.id,
        owner_id=orm_group.owner_id,
        name=orm_group.name,
        description=orm_group.description,
        created_at=orm_group.created_at,
    )

class SqlAlchemyGroupRepository(GroupRepository):
    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def find_by_id(self, id: UUID) -> Optional[DomainGroup]:
        async with self._session_factory() as session:
            orm = await session.get(ORMGroup, id)
            return group_from_orm(orm) if orm else None

    async def add(self, group: DomainGroup) -> Optional[DomainGroup]:
        data = group.to_orm_dict()
        orm = ORMGroup(**data)
        async with self._session_factory() as session:
            session.add(orm)
            await session.commit()
            await session.refresh(orm)
            return group_from_orm(orm) if orm else None
    
    async def delete(self, id: UUID) -> None:
        async with self._session_factory() as session:
            orm = await session.get(ORMGroup, id)
            if not orm:
                return
            await session.delete(orm)
            await session.commit()
    
    async def update(self, group: DomainGroup) -> Optional[DomainGroup]:
        async with self._session_factory() as session:
            orm = await session.get(ORMGroup, group.id)
            if not orm:
                raise NotFoundError(f"Groupe {group.id} not found")
            for key, value in group.to_orm_dict().items():
                setattr(orm, key, value)
            await session.commit()
            return group_from_orm(orm) if orm else None

    async def add_member(self, group_id: UUID, user_id: UUID) -> None:
        async with self._session_factory() as session:
            orm_group = await session.get(ORMGroup, group_id)
            if not orm_group:
                raise NotFoundError(f"Groupe {group_id} not found")
            orm_profile = await session.get(ORMProfile, user_id)
            if not orm_profile:
                raise NotFoundError(f"Profile {user_id} not found")
            if orm_profile not in orm_group.users:
                orm_group.users.append(orm_profile)
                await session.commit()

    async def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        async with self._session_factory() as session:
            orm_group = await session.get(ORMGroup, group_id)
            if not orm_group:
                raise NotFoundError(f"Groupe {group_id} not found")
            orm_profile = await session.get(ORMProfile, user_id)
            if not orm_profile:
                raise NotFoundError(f"Profile {user_id} not found")
            if orm_profile in orm_group.users:
                orm_group.users.remove(orm_profile)
                await session.commit()

    async def list_members(self, group_id: UUID) -> List[DomainProfile]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ORMGroup)
                .options(selectinload(ORMGroup.users))
                .filter(ORMGroup.id == group_id)
            )
            orm_grp = result.scalars().first()
            if not orm_grp:
                raise NotFoundError(f"Groupe {group_id} introuvable")
            return [profil_from_orm(p) for p in orm_grp.users]
    
    async def find_by_owner_id(self, owner_id: UUID) -> Optional[List[DomainGroup]]:
        async with self._session_factory() as session:
            result = await session.execute(select(ORMGroup).filter(ORMGroup.owner_id == owner_id))
            orms = result.scalars().all()
            return [group_from_orm(orm) for orm in orms] if orms else []
    
    async def find_all_groups(self) -> Optional[List[DomainGroup]]:
        async with self._session_factory() as session:
            result = await session.execute(select(ORMGroup))
            orms = result.scalars().all()
            return [group_from_orm(orm) for orm in orms] if orms else []

    async def find_groups_by_member_id(self, user_id: UUID) -> Optional[List[DomainGroup]]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ORMGroup)
                .join(group_users)
                .filter(group_users.c.profile_id == user_id)
            )
            orms = result.scalars().all()
            return [group_from_orm(orm) for orm in orms] if orms else []