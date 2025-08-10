from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.container import container
from src.domain.exceptions import NotFoundError
from src.domain.lib.jwt_manager import decode_access_token, TokenExpiredError, TokenInvalidError
from uuid import UUID
from typing import TypedDict, List

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:

    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = decode_access_token(token)
        return payload
    except TokenExpiredError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TokenInvalidError as e:
        raise HTTPException(status_code=401, detail=str(e))


class UserPayload(TypedDict):
    sub: str
    roles: "list[str]"

def require_owner_or_admin(
    profile_id: UUID,
    user: UserPayload = Depends(get_current_user),
) -> UserPayload:

    user_id = user["sub"]
    roles   = user["roles"]

    if str(user_id) != str(profile_id) and "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )
    return user

async def require_group_owner_or_admin(
    group_id: UUID,
    user: UserPayload = Depends(get_current_user),
) -> UserPayload:

    svc = container.get_group_service()
    try:
        group = await svc.get_by_id(group_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {group_id} not found"
        )

    
    if str(group.owner_id) != user["sub"] and "admin" not in user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: not owner or admin"
        )

    return group

async def require_exercice_owner_or_admin(
    exercise_id: UUID,
    user: UserPayload = Depends(get_current_user),
) -> UserPayload:

    svc = container.get_exercise_service()
    try:
        exercise = await svc.get_by_id(exercise_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise {exercise_id} not found"
        )

    if str(exercise.owner_id) != user["sub"] and "admin" not in user["roles"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: not owner or admin"
        )

    return exercise

async def require_coach_for_user_or_admin(
    target_user_id: UUID,
    user: UserPayload = Depends(get_current_user),
) -> UserPayload:

    profile_svc = container.get_profile_service()
    try:
        target_profile = await profile_svc.get_by_id(target_user_id)  # ✅ Ajout d'await
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {target_user_id} not found"
        )

    roles   = user.get("roles", [])
    user_sub = user.get("sub")

    if "admin" in roles:
        return user

    if "coach" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only coaches or admins can do this"
        )

    group_svc = container.get_group_service()
    try:
        coach_groups = await group_svc.list_owner_groups(UUID(user_sub))  # ✅ Ajout d'await
    except NotFoundError:
        coach_groups = []

    for grp in coach_groups:
        try:
            members = await group_svc.list_members(grp.id)  # ✅ Ajout d'await
        except NotFoundError:
            continue
        if any(m.id == target_user_id for m in members):
            return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="This user is not one of your clients"
    )


async def require_training_owner_or_coach_or_admin(
    training_id: UUID,
    user: UserPayload = Depends(get_current_user),
) -> UserPayload:
    
    roles   = user.get("roles", [])
    sub = user.get("sub")

    if "admin" in roles:
        return user

    svc = container.get_training_service()
    try:
        training = await svc.get_training(training_id)  # ✅ Ajout d'await
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training {training_id} not found"
        )

    if str(training.owner_id) == sub:
        return user

    if "coach" in roles:
        group_svc = container.get_group_service()
        try:
            coach_groups = await group_svc.list_owner_groups(UUID(sub))  # ✅ Ajout d'await
            for grp in coach_groups:
                try:
                    members = await group_svc.list_members(grp.id)  # ✅ Ajout d'await
                    if any(m.id == training.owner_id for m in members):
                        return user
                except NotFoundError:
                    continue
        except NotFoundError:
            pass

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: not owner, coach, or admin"
    )

async def require_training_owner_or_admin(
    training_id: UUID,
    user: dict = Depends(get_current_user),
):
    svc = container.get_training_service()
    try:
        training = await svc.get_training(training_id)
    except NotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Training {training_id} not found")

    sub = user["sub"]
    roles = user["roles"]

    if str(training.owner_id) != sub and "admin" not in roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied: not owner, or admin")
    return training


async def require_owner_coach_for_user_or_admin(
    target_user_id: UUID,
    user: UserPayload = Depends(get_current_user),
):

    profile_svc = container.get_profile_service()
    try:
        target_profile = await profile_svc.get_by_id(target_user_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {target_user_id} not found"
        )

    roles = user.get("roles", [])
    sub   = user.get("sub")

    if sub == str(target_user_id):
        return target_profile

    if "admin" in roles:
        return target_profile

    return await require_coach_for_user_or_admin(target_user_id, user)