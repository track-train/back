from typing import Optional, List
from sqlalchemy.orm import Session
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
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, id: UUID) -> Optional[DomainGroup]:
        orm = self._session.get(ORMGroup, id)
        return group_from_orm(orm) if orm else None

    def add(self, group: DomainGroup) -> Optional[DomainGroup]:
        data = group.to_orm_dict()
        orm = ORMGroup(**data)
        self._session.add(orm)
        self._session.commit()
        self._session.refresh(orm)
        return group_from_orm(orm) if orm else None
    
    def delete(self, id: UUID) -> None:
        orm = self._session.get(ORMGroup, id)
        if not orm:
            return
        self._session.delete(orm)
        self._session.commit()
    
    def update(self, group: DomainGroup) -> Optional[DomainGroup]:
        orm = self._session.get(ORMGroup, group.id)
        if not orm:
            raise NotFoundError(f"Groupe {group.id} not found")
        for key, value in group.to_orm_dict().items():
            setattr(orm, key, value)
        self._session.commit()
        return group_from_orm(orm) if orm else None

    
    def add_member(self, group_id: UUID, user_id: UUID) -> None:
        orm_group = self._session.get(ORMGroup, group_id)
        if not orm_group:
            raise NotFoundError(f"Groupe {group_id} not found")
        orm_profile = self._session.get(ORMProfile, user_id)
        if not orm_profile:
            raise NotFoundError(f"Profile {user_id} not found")
        if orm_profile not in orm_group.users:
            orm_group.users.append(orm_profile)
            self._session.commit()

    def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        orm_group = self._session.get(ORMGroup, group_id)
        if not orm_group:
            raise NotFoundError(f"Groupe {group_id} not found")
        orm_profile = self._session.get(ORMProfile, user_id)
        if not orm_profile:
            raise NotFoundError(f"Profile {user_id} not found")
        if orm_profile in orm_group.users:
            orm_group.users.remove(orm_profile)
            self._session.commit()

    def list_members(self, group_id: UUID) -> List[DomainProfile]:
        orm_grp = self._session.get(ORMGroup, group_id)
        if not orm_grp:
            raise NotFoundError(f"Groupe {group_id} introuvable")
        return [profil_from_orm(p) for p in orm_grp.users]
    
    def find_by_owner_id(self, owner_id: UUID) -> Optional[List[DomainGroup]]:
        orms = self._session.query(ORMGroup).filter(ORMGroup.owner_id == owner_id).all()
        return [group_from_orm(orm) for orm in orms] if orms else []
    
    def find_all_groups(self) -> Optional[List[DomainGroup]]:
        orms = self._session.query(ORMGroup).all()
        return [group_from_orm(orm) for orm in orms] if orms else []