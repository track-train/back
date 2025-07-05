from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from src.entrypoints.api.schemas.profile import ProfileCreate, ProfileRead
from src.domain.commands.create_profile import CreateProfileCommand
from src.domain.command_handlers.create_profile_handler import CreateProfileHandler
from src.domain.exceptions import DuplicateProfileError
from src.adapters.sqlalchemy.repositories import SqlAlchemyProfileRepository
from src.adapters.security import BcryptPasswordHasher
from src.entrypoints.api.deps import get_db_session

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    dto: ProfileCreate,
    session: Session = Depends(get_db_session),
):
    repo   = SqlAlchemyProfileRepository(session)
    hasher = BcryptPasswordHasher()
    handler = CreateProfileHandler(repo, hasher)

    cmd = CreateProfileCommand(**dto.dict())
    try:
        profile = handler.handle(cmd)
    except DuplicateProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return profile