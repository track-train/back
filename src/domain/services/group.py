from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

from src.domain.model.group import Group as DomainGroup
from src.domain.model.profile import Profile as DomainProfile
from src.domain.ports.group_repository import GroupRepository
from src.domain.exceptions import  NotFoundError

class GroupService:
    def __init__(self, repo: GroupRepository):
        self._repo = repo

    def create(self, *,
               owner_id: UUID,
               name: str,
               description: Optional[str] = None) -> DomainGroup:
        if not name:
            raise ValueError("Group name cannot be empty")

        group = DomainGroup(
            id=uuid4(),
            owner_id=owner_id,
            name=name,
            description=description,
            created_at=datetime.utcnow(),
        )

        return self._repo.add(group)

    def delete(self, group_id: UUID):
        group = self._repo.find_by_id(group_id)
        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")
        
        self._repo.delete(group_id)
    
    def update(self, group: DomainGroup) -> DomainGroup:
        existing_group = self._repo.find_by_id(group.id)
        if not existing_group:
            raise NotFoundError(f"Group with id {group.id} not found")
        
        return self._repo.update(group)
    
    def add_member(self, group_id: UUID, user_id: UUID) -> None:
        group = self._repo.find_by_id(group_id)
        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")
        
        self._repo.add_member(group_id, user_id)

    def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        group = self._repo.find_by_id(group_id)
        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")
        
        profiles = self._repo.list_members(group_id) 
        member_ids = [p.id for p in profiles] 
        if user_id not in member_ids:
            raise NotFoundError(f"User with id {user_id} is not a member of group {group_id}")
        
        self._repo.remove_member(group_id, user_id)
    
    def list_owner_groups(self, owner_id: UUID) -> List[DomainGroup]:
        groups = self._repo.find_by_owner_id(owner_id)
        if not groups:
            raise NotFoundError(f"No groups found for owner with id {owner_id}")
        
        return groups

    def list_members(self, group_id: UUID) -> List[DomainProfile]:
        group = self._repo.find_by_id(group_id)
        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")
        
        return self._repo.list_members(group_id) or []
    
    def get_all_groups(self) -> List[DomainGroup]:
        groups = self._repo.find_all_groups()
        if not groups:
            raise NotFoundError("No groups found")
        
        return groups