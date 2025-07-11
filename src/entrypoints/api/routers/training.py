from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND
from sqlalchemy.sql.functions import user

from src.entrypoints.api.deps.auth import get_current_user, require_coach_or_admin_for_user, require_training_owner_or_coach_or_admin
from src.entrypoints.api.schemas.training import TrainingRead, TrainingCreate, TrainingUpdate
from src.domain.exceptions import NotFoundError
from src.container import container

router = APIRouter(prefix="/trainings", tags=["trainings"])

@router.get("/mine", response_model=List[TrainingRead], dependencies=[Depends(get_current_user)])
def get_my_trainings(user=Depends(get_current_user)):
    service = container.get_training_service()
    try:
        owner_id = UUID(user["sub"])
        trainings = service.get_all_owner_trainings(owner_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Trainings for user {owner_id} not found")

    return [TrainingRead.model_validate(t) for t in trainings]

@router.get("/user/{target_user_id}", response_model=List[TrainingRead], dependencies=[Depends(require_coach_or_admin_for_user)])
def get_user_trainings(target_user_id: UUID, user=Depends(get_current_user)):
    service = container.get_training_service()
    try:
        trainings = service.get_all_owner_trainings(target_user_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Trainings for user {target_user_id} not found")
    
    return [TrainingRead.model_validate(t) for t in trainings]

@router.get("/{training_id}", response_model=TrainingRead, dependencies=[Depends(require_training_owner_or_coach_or_admin)])
def get_training(training_id: UUID, user=Depends(get_current_user)):
    service = container.get_training_service()
    try:
        training = service.get_training(training_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Training {training_id} not found")
    
    return TrainingRead.model_validate(training)



@router.post("/{target_user_id}", response_model=TrainingRead, status_code=201)
def create_training(target_user_id: UUID, dto: TrainingCreate, _=Depends(require_coach_or_admin_for_user)):
    service = container.get_training_service()
    
    try:
        training = service.create_training(
            owner_id=target_user_id,
            name=dto.name,
            description=dto.description
        )
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"User {target_user_id} not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return TrainingRead.model_validate(training)


@router.patch("/{training_id}/user/{target_user_id}", response_model=TrainingRead)
def update_training(
    training_id: UUID,
    target_user_id: UUID,
    dto: TrainingUpdate,
    _ = Depends(require_coach_or_admin_for_user),
):
    svc = container.get_training_service()
    try:
        updated = svc.update_training(
            training_id=training_id,
            name=dto.name,
            description=dto.description,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found"
        )
    return TrainingRead.model_validate(updated)

@router.delete("/{training_id}/user/{target_user_id}", status_code=204)
def delete_training(training_id: UUID, user=Depends(require_coach_or_admin_for_user)):
    service = container.get_training_service()
    
    try:
        service.delete_training(training_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Training {training_id} not found")
    
    return {"detail": "Training deleted successfully"}


    