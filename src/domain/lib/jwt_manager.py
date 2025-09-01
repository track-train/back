
import os
from datetime import datetime, timedelta
from typing import Optional, List

from jose import JWTError, jwt

from src.domain.exceptions import TokenInvalidError, TokenExpiredError


SECRET_KEY = os.getenv("SECRET_KEY", "change_me_please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def create_access_token(
    subject: str,
    roles: List[str],
    expires_delta: Optional[timedelta] = None
) -> str:

    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "sub": subject,
        "roles": roles,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        if "Signature has expired" in str(e):
            raise TokenExpiredError("Token expired") from e
        raise TokenInvalidError("Invalid JWT") from e
