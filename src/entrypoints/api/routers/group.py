from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from sqlalchemy.sql.functions import user
from starlette.status import HTTP_404_NOT_FOUND
from src.domain.exceptions import NotFoundError
from src.entrypoints.api.deps.auth import require_group_owner_or_admin, get_current_user
from src.entrypoints.api.deps.roles import require_roles
from src.entrypoints.api.schemas.group import GroupCreate, GroupUpdate, GroupRead, GroupMember
from src.entrypoints.api.schemas.profile import CoachProfileRead
from src.container import container


router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("", response_model=GroupRead, status_code=201, dependencies=[Depends(require_roles("admin", "coach"))])
async def create_group(
    dto: GroupCreate,
    user=Depends(get_current_user)
):
    service = container.get_group_service()
    grp = await await service.create(owner_id=UUID(user["sub"]), name=dto.name, description=dto.description)
    return GroupRead.model_validate(grp)

@router.get("", response_model=List[GroupRead], dependencies=[Depends(get_current_user)])
async def list_groups():
    service = container.get_group_service()
    try:
        groups = await await service.get_all_groups()
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    return [GroupRead.model_validate(g) for g in groups]

@router.get("/{group_id}", response_model=GroupRead, dependencies=[Depends(get_current_user)])
async def get_group(group_id: UUID):
    service = container.get_group_service()
    grp = service._repo.find_by_id(group_id)
    if not grp:
        raise HTTPException(404, "Group not found")
    return GroupRead.model_validate(grp)


@router.patch("/{group_id}", response_model=GroupRead, dependencies=[Depends(require_group_owner_or_admin)])
async def patch_group(group_id: UUID, dto: GroupUpdate):
    service = container.get_group_service()
    existing = service._repo.find_by_id(group_id)
    if not existing:
        raise HTTPException(404, "Group not found")
    updated = existing
    if dto.name is not None:
        updated.name = dto.name
    if dto.description is not None:
        updated.description = dto.description
    grp = await service.update(updated)
    return GroupRead.model_validate(grp)

@router.delete("/{group_id}", status_code=204, dependencies=[Depends(require_group_owner_or_admin)])
async def delete_group(group_id: UUID):
    service = container.get_group_service()
    try:
        await service.delete(group_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))

@router.post("/{group_id}/members/{user_id}", status_code=204, dependencies=[Depends(require_group_owner_or_admin)])
async def add_member(group_id: UUID, user_id: UUID):
    service = container.get_group_service()
    try:
        await service.add_member(group_id, user_id)
    except (NotFoundError) as e:
        raise HTTPException(404, str(e))

@router.delete("/{group_id}/members/{user_id}", status_code=204, dependencies=[Depends(require_group_owner_or_admin)])
async def remove_member(group_id: UUID, user_id: UUID):
    service = container.get_group_service()
    try:
        await service.remove_member(group_id, user_id)
    except (NotFoundError) as e:
        raise HTTPException(404, str(e))

@router.get("/{group_id}/members", response_model=List[GroupMember], dependencies=[Depends(require_group_owner_or_admin)])
async def list_members(group_id: UUID):
    service = container.get_group_service()
    try:
        members = await service.list_members(group_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    return [GroupMember.model_validate(p) for p in members]

@router.get("/owner/{owner_id}", response_model=List[GroupRead], dependencies=[Depends(get_current_user)])
async def list_owner_groups(owner_id: UUID):
    service = container.get_group_service()
    try:
        groups = await service.list_owner_groups(owner_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    return [GroupRead.model_validate(g) for g in groups]

@router.delete("/{group_id}/leave", status_code=204)
async def leave_group(group_id: UUID, user=Depends(get_current_user)):
    service = container.get_group_service()
    try:
        await service.remove_member(group_id, UUID(user["sub"]))
    except NotFoundError as e:
        raise HTTPException(404, str(e))

@router.get("/coachs/mine", response_model=List[CoachProfileRead])
async def get_my_coaches(user=Depends(get_current_user)):
    service = container.get_group_service()
    try:
        coaches = await service.get_my_coaches(UUID(user["sub"]))
        return [CoachProfileRead.model_validate(coach) for coach in coaches]
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    
