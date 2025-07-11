from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.container import container
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
            detail="Forbidden access"
        )
    return user

def require_group_owner_or_admin(
    group_id: UUID,
    user: UserPayload = Depends(get_current_user),
) -> UserPayload:

    svc = container.get_group_service()
    try:
        group = svc._repo.find_by_id(group_id)
    except Exception:
        group = None

    if not group:
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

def require_exercice_owner_or_admin(
    exercise_id: UUID,
    user: UserPayload = Depends(get_current_user),
) -> UserPayload:

    svc = container.get_exercise_service()
    try:
        exercise = svc._repo.find_by_id(exercise_id)
    except Exception:
        exercise = None

    if not exercise:
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