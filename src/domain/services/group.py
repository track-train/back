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

    async def create(self, *,
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

        return await self._repo.add(group)

    async def delete(self, group_id: UUID):
        group = await self._repo.find_by_id(group_id)
        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")
        
        await self._repo.delete(group_id)
    
    async def update(self, group: DomainGroup) -> DomainGroup:
        existing_group = await self._repo.find_by_id(group.id)
        if not existing_group:
            raise NotFoundError(f"Group with id {group.id} not found")
        
        return await self._repo.update(group)
    
    async def add_member(self, group_id: UUID, user_id: UUID) -> None:
        # Vérifier que le groupe existe
        group = await self._repo.find_by_id(group_id)
        if not group:
            raise NotFoundError(f"Group {group_id} not found")
        
        # Vérifier que l'utilisateur existe
        from src.container import container
        profile_service = container.get_profile_service()  # ou injection via constructeur
        try:
            user = await profile_service.get_by_id(user_id)
        except NotFoundError:
            raise NotFoundError(f"User {user_id} not found")
        
        # Ajouter le membre
        await self._repo.add_member(group_id, user_id)

    async def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        group = await self._repo.find_by_id(group_id)
        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")
        
        profiles = await self._repo.list_members(group_id) 
        member_ids = [p.id for p in profiles] 
        if user_id not in member_ids:
            raise NotFoundError(f"User with id {user_id} is not a member of group {group_id}")
        
        await self._repo.remove_member(group_id, user_id)
    
    async def list_owner_groups(self, owner_id: UUID) -> List[DomainGroup]:
        groups = await self._repo.find_by_owner_id(owner_id)
        if not groups:
            raise NotFoundError(f"No groups found for owner with id {owner_id}")
        
        return groups

    async def list_members(self, group_id: UUID) -> List[DomainProfile]:
        group = await self._repo.find_by_id(group_id)
        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")
        
        return await self._repo.list_members(group_id) or []
    
    async def get_all_groups(self) -> List[DomainGroup]:
        groups = await self._repo.find_all_groups()
        if not groups:
            raise NotFoundError("No groups found")
        
        return groups

    async def get_by_id(self, group_id: UUID) -> DomainGroup:
        group = await self._repo.find_by_id(group_id)
        if not group:
            raise NotFoundError(f"Group with id {group_id} not found")
        return group

    async def get_my_coaches(self, user_id: UUID) -> List[DomainProfile]:
        groups = await self._repo.find_groups_by_member_id(user_id)
        if not groups:
            raise NotFoundError(f"No groups found for user {user_id}")
        
        coach_ids = set()
        for group in groups:
            coach_ids.add(group.owner_id)
        
        from src.container import container
        profile_service = container.get_profile_service()
        
        coaches = []
        for coach_id in coach_ids:
            try:
                coach = await profile_service.get_by_id(coach_id)
                if coach and "coach" in coach.roles:
                    coaches.append(coach)
            except NotFoundError:
                continue
        
        if not coaches:
            raise NotFoundError("No coaches found in your groups")
                
        return coaches