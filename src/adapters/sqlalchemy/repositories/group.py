from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, id: UUID) -> Optional[DomainGroup]:
        orm = await self._session.get(ORMGroup, id)
        return group_from_orm(orm) if orm else None

    async def add(self, group: DomainGroup) -> Optional[DomainGroup]:
        data = group.to_orm_dict()
        orm = ORMGroup(**data)
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return group_from_orm(orm) if orm else None
    
    async def delete(self, id: UUID) -> None:
        orm = await self._session.get(ORMGroup, id)
        if not orm:
            return
        await self._session.delete(orm)
        await self._session.commit()
    
    async def update(self, group: DomainGroup) -> Optional[DomainGroup]:
        orm = await self._session.get(ORMGroup, group.id)
        if not orm:
            raise NotFoundError(f"Groupe {group.id} not found")
        for key, value in group.to_orm_dict().items():
            setattr(orm, key, value)
        await self._session.commit()
        return group_from_orm(orm) if orm else None

    
    async def add_member(self, group_id: UUID, user_id: UUID) -> None:
        async with self._session_factory() as session:
            # Vérifier que le groupe existe
            group_stmt = select(ORMGroup).where(ORMGroup.id == group_id)
            group_result = await session.execute(group_stmt)
            group = group_result.scalar_one_or_none()
            
            if not group:
                raise NotFoundError(f"Group {group_id} not found")
            
            # Vérifier que l'utilisateur existe
            user_stmt = select(ORMProfile).where(ORMProfile.id == user_id)
            user_result = await session.execute(user_stmt)
            user = user_result.scalar_one_or_none()
            
            if not user:
                raise NotFoundError(f"User {user_id} not found")
            
            # Vérifier que l'utilisateur n'est pas déjà membre
            existing_stmt = select(group_users).where(
                (group_users.c.group_id == group_id) & 
                (group_users.c.profile_id == user_id)
            )
            existing_result = await session.execute(existing_stmt)
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                return  # Déjà membre, on ne fait rien
            
            # Ajouter la relation
            insert_stmt = group_users.insert().values(
                group_id=group_id,
                profile_id=user_id
            )
            await session.execute(insert_stmt)
            await session.commit()

    async def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        orm_group = await self._session.get(ORMGroup, group_id)
        if not orm_group:
            raise NotFoundError(f"Groupe {group_id} not found")
        orm_profile = await self._session.get(ORMProfile, user_id)
        if not orm_profile:
            raise NotFoundError(f"Profile {user_id} not found")
        if orm_profile in orm_group.users:
            orm_group.users.remove(orm_profile)
            await self._session.commit()

    async def list_members(self, group_id: UUID) -> List[DomainProfile]:
        orm_grp = await self._session.get(ORMGroup, group_id)
        if not orm_grp:
            raise NotFoundError(f"Groupe {group_id} introuvable")
        return [profil_from_orm(p) for p in orm_grp.users]
    
    async def find_by_owner_id(self, owner_id: UUID) -> Optional[List[DomainGroup]]:
        stmt = select(ORMGroup).where(ORMGroup.owner_id == owner_id)
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [group_from_orm(orm) for orm in orms] if orms else []
    
    async def find_all_groups(self) -> Optional[List[DomainGroup]]:
        stmt = select(ORMGroup)
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [group_from_orm(orm) for orm in orms] if orms else []

    async def find_groups_by_member_id(self, user_id: UUID) -> Optional[List[DomainGroup]]:
        stmt = select(ORMGroup).join(group_users).where(group_users.c.profile_id == user_id)
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [group_from_orm(orm) for orm in orms] if orms else []