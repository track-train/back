from uuid import UUID, uuid4
from typing import Optional, List
import datetime

from src.domain.model.group import Group as DomainGroup
from src.domain.model.profile import Profile as DomainProfile
from src.domain.ports.group_repository import GroupRepository
from src.domain.exceptions import NotFoundError
from src.adapters.inmemory.repositories.profile import InMemoryProfileRepository

class InMemoryGroupRepository(GroupRepository):
    def __init__(self, profile_repo: InMemoryProfileRepository):
        self._groups: dict[UUID, DomainGroup] = {}
        self._members: dict[UUID, List[UUID]] = {}
        self._profile_repo = profile_repo        

    def find_by_id(self, id: UUID) -> Optional[DomainGroup]:
        return self._groups.get(id)

    def add(self, group: DomainGroup) -> Optional[DomainGroup]:
        new_id = uuid4()
        group.id = new_id
        if not getattr(group, 'created_at', None):
            group.created_at = datetime.datetime.utcnow()
        self._groups[new_id] = group
        self._members[new_id] = []
        return group

    def delete(self, id: UUID) -> None:
        self._groups.pop(id, None)
        self._members.pop(id, None)

    def update(self, group: DomainGroup) -> Optional[DomainGroup]:
        if group.id not in self._groups:
            raise NotFoundError(f"Groupe {group.id} not found")
        self._groups[group.id] = group
        return group

    def add_member(self, group_id: UUID, user_id: UUID) -> None:
        if group_id not in self._groups:
            raise NotFoundError(f"Groupe {group_id} not found")
        user = self._profile_repo.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"Profile {user_id} not found")
        members = self._members.setdefault(group_id, [])
        if user_id not in members:
            members.append(user_id)

    def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        if group_id not in self._groups:
            raise NotFoundError(f"Groupe {group_id} not found")
        members = self._members.get(group_id, [])
        if user_id not in members:
            raise NotFoundError(f"Profile {user_id} not found in group {group_id}")
        members.remove(user_id)

    def list_members(self, group_id: UUID) -> List[DomainProfile]:
        if group_id not in self._groups:
            raise NotFoundError(f"Groupe {group_id} introuvable")
        user_ids = self._members.get(group_id, [])
        return [self._profile_repo.find_by_id(uid) for uid in user_ids if self._profile_repo.find_by_id(uid)]

    def find_by_owner_id(self, owner_id: UUID) -> Optional[List[DomainGroup]]:
        return [g for g in self._groups.values() if g.owner_id == owner_id]

    def find_all_groups(self) -> Optional[List[DomainGroup]]:
        return list(self._groups.values())

    def find_groups_by_member_id(self, user_id: UUID) -> Optional[List[DomainGroup]]:
        groups = []
        for group_id, member_ids in self._members.items():
            if user_id in member_ids:
                groups.append(self._groups[group_id])
        return groups if groups else []
