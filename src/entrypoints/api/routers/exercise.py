from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from typing import List

from sqlalchemy.sql.functions import user
from starlette.status import HTTP_404_NOT_FOUND
from src.domain.exceptions import NotFoundError
from src.entrypoints.api.deps.auth import require_group_owner_or_admin, get_current_user, require_exercice_owner_or_admin
from src.entrypoints.api.schemas.exercise import ExerciseCreate, ExerciseUpdate, ExerciseRead
from src.entrypoints.api.deps.roles import require_roles
from src.container import container

router = APIRouter(prefix="/exercises", tags=["exercises"])

@router.post("", response_model=ExerciseRead, status_code=201, dependencies=[Depends(require_roles("admin", "coach"))])
async def create_exercise(
    dto: ExerciseCreate,
    user=Depends(get_current_user)
):
    service = container.get_exercise_service()
    
    try: 
        exercise = await service.create_exercise(
            owner_id=UUID(user["sub"]),
            name=dto.name,
            description=dto.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return ExerciseRead.model_validate(exercise)

@router.get("", response_model=List[ExerciseRead], dependencies=[Depends(require_roles("admin", "coach"))])
async def get_exercises():
    service = container.get_exercise_service()
    try:
        exercises = await service.get_all_exercises()
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    return [ExerciseRead.model_validate(e) for e in exercises]

@router.get("/mine", response_model=List[ExerciseRead], dependencies=[Depends(get_current_user)])
async def get_my_exercises(
    user=Depends(get_current_user)
):
    service = container.get_exercise_service()
    try:
        owner_id = UUID(user["sub"])
        exercises = await service.get_all_owner_exercises(owner_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    
    return [ExerciseRead.model_validate(e) for e in exercises]

@router.get("/{exercise_id}", response_model=ExerciseRead, dependencies=[Depends(require_exercice_owner_or_admin)])
async def get_exercise(
    exercise_id: UUID
):
    service = container.get_exercise_service()
    try:
        exercise = await service.get_exercise(exercise_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    
    return ExerciseRead.model_validate(exercise)

@router.patch("/{exercise_id}", response_model=ExerciseRead, dependencies=[Depends(require_exercice_owner_or_admin)])
async def update_exercise(
    exercise_id: UUID,
    dto: ExerciseUpdate
):
    service = container.get_exercise_service()
    try:
        exercise = await service.update_exercise(
            exercise_id=exercise_id,
            name=dto.name,
            description=dto.description
        )
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    
    return ExerciseRead.model_validate(exercise)

@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_exercice_owner_or_admin)])
async def delete_exercise(
    exercise_id: UUID
):
    service = container.get_exercise_service()
    try:
        await service.delete_exercise(exercise_id)
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    
    return None