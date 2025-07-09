from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.domain.lib.jwt_manager import decode_access_token, TokenExpiredError, TokenInvalidError

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
