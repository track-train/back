from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND

from src.container import container
from src.entrypoints.api.schemas.diet import DietCreate, DietRead, DietUpdate, MacroPlanCreate, MacroPlanRead, MacroPlanUpdate, MealPlanCreate, MealPlanRead, MealPlanUpdate
from src.domain.exceptions import NotFoundError
from src.entrypoints.api.deps.auth import UserPayload, get_current_user, require_coach_for_user_or_admin, require_owner_coach_for_user_or_admin
from src.container import container

router = APIRouter(prefix="/diets", tags=["diets"])

@router.get("/mine", response_model=List[DietRead], dependencies=[Depends(get_current_user)])
async def get_my_diets(user=Depends(get_current_user)):
    svc = container.get_diet_service()
    owner_id = UUID(user["sub"])
    diets = await svc.list_owner_diets(owner_id)
    return [DietRead.model_validate(d) for d in diets]

@router.get("/user/{target_user_id}", response_model=List[DietRead],
            dependencies=[Depends(require_coach_for_user_or_admin)])
async def get_user_diets(target_user_id: UUID):
    svc = container.get_diet_service()
    diets = await svc.list_owner_diets(target_user_id)
    return [DietRead.model_validate(d) for d in diets]


@router.post("/{target_user_id}", response_model=DietRead, status_code=status.HTTP_201_CREATED)
async def create_diet(target_user_id: UUID,
                dto: DietCreate,
                _=Depends(require_coach_for_user_or_admin)):
    svc = container.get_diet_service()
    try:
        d = await svc.create_diet(
            owner_id=target_user_id,
            name=dto.name,
            description=dto.description or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return DietRead.model_validate(d)

@router.patch("/{diet_id}/user/{target_user_id}", response_model=DietRead)
async def update_diet(diet_id: UUID,
                target_user_id: UUID,
                dto: DietUpdate,
                _=Depends(require_coach_for_user_or_admin)):
    svc = container.get_diet_service()
    try:
        updated = await svc.update_diet(
            diet_id=diet_id,
            name=dto.name,
            description=dto.description
        )
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Diet not found")
    return DietRead.model_validate(updated)

@router.get(
    "/{diet_id}",
    response_model=DietRead,
    dependencies=[Depends(get_current_user)]
)
async def get_diet(diet_id: UUID):
    svc = container.get_diet_service()
    try:
        diet = await svc.get_diet(diet_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Diet not found")
    return DietRead.model_validate(diet)

@router.delete("/{diet_id}/user/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diet(diet_id: UUID,
                _=Depends(require_coach_for_user_or_admin)):
    svc = container.get_diet_service()
    try:
        await svc.delete_diet(diet_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Diet not found")



@router.get(
    "/{diet_id}/user/{target_user_id}/macro_plans",
    response_model=List[MacroPlanRead],
    dependencies=[Depends(require_owner_coach_for_user_or_admin)]
)
async def list_macro_plans(diet_id: UUID, target_user_id: UUID):
    svc = container.get_diet_service()
    plans = await svc.get_macro_plans_for_diet(diet_id)
    return [MacroPlanRead.model_validate(p) for p in plans]

@router.get(
    "/{diet_id}/user/{target_user_id}/macro_plans/{plan_id}",
    response_model=MacroPlanRead,
    dependencies=[Depends(require_owner_coach_for_user_or_admin)]
)
async def get_macro_plan(diet_id: UUID, target_user_id: UUID, plan_id: UUID):
    svc = container.get_diet_service()
    try:
        p = await svc.get_macro_plan(plan_id)
    except NotFoundError:
        raise HTTPException(HTTP_404_NOT_FOUND, f"MacroPlan {plan_id} not found")
    return MacroPlanRead.model_validate(p)

@router.post(
    "/{diet_id}/user/{target_user_id}/macro_plans",
    response_model=MacroPlanRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_coach_for_user_or_admin)]
)
async def create_macro_plan(
    diet_id: UUID,
    target_user_id: UUID,
    dto: MacroPlanCreate
):
    svc = container.get_diet_service()
    try:
        p = await svc.create_macro_plan(
            diet_id=diet_id,
            name=dto.name,
            carbohydrates=dto.carbohydrates,
            lipids=dto.lipids,
            protein=dto.protein,
            fiber=dto.fiber,
            water=dto.water,
            kilocalorie=dto.kilocalorie,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MacroPlanRead.model_validate(p)

@router.get("/macro_plans/mine", response_model=List[MacroPlanRead], dependencies=[Depends(get_current_user)])
async def list_my_macro_plans(user: UserPayload = Depends(get_current_user)):
    svc = container.get_diet_service()
    plans = await svc.get_macro_plans_by_user_id(UUID(user["sub"]))
    return [MacroPlanRead.model_validate(p) for p in plans]

@router.patch(
    "/{diet_id}/user/{target_user_id}/macro_plans/{plan_id}",
    response_model=MacroPlanRead,
    dependencies=[Depends(require_coach_for_user_or_admin)]
)
async def update_macro_plan(
    diet_id: UUID,
    target_user_id: UUID,
    plan_id: UUID,
    dto: MacroPlanUpdate
):
    svc = container.get_diet_service()
    try:
        updated = await svc.update_macro_plan(
            plan_id=plan_id,
            name=dto.name,
            carbohydrates=dto.carbohydrates,
            lipids=dto.lipids,
            protein=dto.protein,
            fiber=dto.fiber,
            water=dto.water,
            kilocalorie=dto.kilocalorie,
        )
    except NotFoundError:
        raise HTTPException(HTTP_404_NOT_FOUND, "MacroPlan not found")
    return MacroPlanRead.model_validate(updated)

@router.delete(
    "/{diet_id}/user/{target_user_id}/macro_plans/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_coach_for_user_or_admin)]
)
async def delete_macro_plan(diet_id: UUID, target_user_id: UUID, plan_id: UUID):
    svc = container.get_diet_service()
    try:
        await svc.delete_macro_plan(plan_id)
    except NotFoundError:
        raise HTTPException(HTTP_404_NOT_FOUND, "MacroPlan not found")
    


@router.get(
    "/{diet_id}/user/{target_user_id}/meal_plans",
    response_model=List[MealPlanRead],
    dependencies=[Depends(require_owner_coach_for_user_or_admin)]
)
async def list_meal_plans(diet_id: UUID, target_user_id: UUID):
    svc = container.get_diet_service()
    plans = await svc.get_meal_plans_by_diet(diet_id)
    return [MealPlanRead.model_validate(p) for p in plans]

@router.get(
    "/{diet_id}/user/{target_user_id}/meal_plans/{plan_id}",
    response_model=MealPlanRead,
    dependencies=[Depends(require_owner_coach_for_user_or_admin)]
)
async def get_meal_plan(diet_id: UUID, target_user_id: UUID, plan_id: UUID):
    svc = container.get_diet_service()
    try:
        mp = await svc.get_meal_plan_by_id(plan_id)
    except NotFoundError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"MealPlan {plan_id} not found"
        )
    return MealPlanRead.model_validate(mp)

@router.post(
    "/{diet_id}/user/{target_user_id}/meal_plans",
    response_model=MealPlanRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_coach_for_user_or_admin)]
)
async def create_meal_plan(
    diet_id: UUID,
    target_user_id: UUID,
    dto: MealPlanCreate
):
    svc = container.get_diet_service()
    try:
        mp = await svc.create_meal_plan(
            diet_id=diet_id,
            name=dto.name,
            meals=dto.meals,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return MealPlanRead.model_validate(mp)

@router.get(
    "/meal_plans/mine",
    response_model=List[MealPlanRead],
    dependencies=[Depends(get_current_user)]
)
async def list_my_meal_plans(user = Depends(get_current_user)):
    svc = container.get_diet_service()
    user_id = UUID(user["sub"])
    plans = await svc.get_meal_plans_by_user(user_id)
    return [MealPlanRead.model_validate(p) for p in plans]

@router.patch(
    "/{diet_id}/user/{target_user_id}/meal_plans/{plan_id}",
    response_model=MealPlanRead,
    dependencies=[Depends(require_coach_for_user_or_admin)]
)
async def update_meal_plan(
    diet_id: UUID,
    target_user_id: UUID,
    plan_id: UUID,
    dto: MealPlanUpdate
):
    svc = container.get_diet_service()
    try:
        updated = await svc.update_meal_plan(
            plan_id=plan_id,
            name=dto.name,
            meals=dto.meals,
        )
    except NotFoundError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="MealPlan not found"
        )
    return MealPlanRead.model_validate(updated)

@router.delete(
    "/{diet_id}/user/{target_user_id}/meal_plans/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_coach_for_user_or_admin)]
)
async def delete_meal_plan(diet_id: UUID, target_user_id: UUID, plan_id: UUID):
    svc = container.get_diet_service()
    try:
        await svc.delete_meal_plan(plan_id)
    except NotFoundError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="MealPlan not found"
        )