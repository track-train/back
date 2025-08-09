from fastapi import Depends, HTTPException, status
from typing import List

from .auth import get_current_user

def require_roles(*allowed_roles: str):

    async def dependency(user: dict = Depends(get_current_user)) -> dict:
        user_roles: List[str] = user.get("roles", [])
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(status_code=403, detail="Access forbidden")
        return user
    return dependency
