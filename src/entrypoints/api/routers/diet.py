from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND

from src.container import container
from src.entrypoints.api.schemas.diet import DietCreate, DietRead, DietUpdate
from src.domain.exceptions import NotFoundError
from src.entrypoints.api.deps.auth import get_current_user, require_coach_or_admin_for_user
from src.container import container

router = APIRouter(prefix="/diets", tags=["diets"])

@router.get("/mine", response_model=List[DietRead], dependencies=[Depends(get_current_user)])
def get_my_diets(user=Depends(get_current_user)):
    svc = container.get_diet_service()
    owner_id = UUID(user["sub"])
    diets = svc.list_owner_diets(owner_id)
    return [DietRead.model_validate(d) for d in diets]

@router.get("/user/{target_user_id}", response_model=List[DietRead],
            dependencies=[Depends(require_coach_or_admin_for_user)])
def get_user_diets(target_user_id: UUID):
    svc = container.get_diet_service()
    diets = svc.list_owner_diets(target_user_id)
    return [DietRead.model_validate(d) for d in diets]


@router.post("/{target_user_id}", response_model=DietRead, status_code=status.HTTP_201_CREATED)
def create_diet(target_user_id: UUID,
                dto: DietCreate,
                _=Depends(require_coach_or_admin_for_user)):
    svc = container.get_diet_service()
    try:
        d = svc.create_diet(
            owner_id=target_user_id,
            name=dto.name,
            description=dto.description or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DietRead.model_validate(d)

@router.patch("/{diet_id}/user/{target_user_id}", response_model=DietRead)
def update_diet(diet_id: UUID,
                target_user_id: UUID,
                dto: DietUpdate,
                _=Depends(require_coach_or_admin_for_user)):
    svc = container.get_diet_service()
    try:
        updated = svc.update_diet(
            diet_id=diet_id,
            name=dto.name,
            description=dto.description
        )
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Diet not found")
    return DietRead.model_validate(updated)

@router.delete("/{diet_id}/user/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diet(diet_id: UUID,
                _=Depends(require_coach_or_admin_for_user)):
    svc = container.get_diet_service()
    try:
        svc.delete_diet(diet_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Diet not found")
