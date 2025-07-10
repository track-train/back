from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
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