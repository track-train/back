from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from src.entrypoints.api.schemas.profile import ProfileCreate, ProfileRead
from src.domain.commands.create_profile import CreateProfileCommand
from src.domain.command_handlers.create_profile_handler import CreateProfileHandler
from src.domain.exceptions import DuplicateProfileError
from src.adapters.sqlalchemy.repositories import SqlAlchemyProfileRepository
from src.adapters.security import BcryptPasswordHasher
from src.entrypoints.api.deps import get_db_session
from src.domain.commands.delete_profile import DeleteProfileCommand
from src.domain.command_handlers.delete_profile_handler import DeleteProfileHandler
from src.domain.exceptions import ProfileNotFoundError

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

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: UUID,
    session: Session = Depends(get_db_session),
):
    repo = SqlAlchemyProfileRepository(session)
    handler = DeleteProfileHandler(repo)

    # 2. On construit la commande métier avec l'UUID reçu en URL
    cmd = DeleteProfileCommand(id=profile_id)

    # 3. On exécute le handler et on gère l'erreur si le profil n'existe pas
    try:
        handler.handle(cmd)
    except ProfileNotFoundError as e:
        # Si l'UUID n'est pas dans la BDD, renvoyer 404
        raise HTTPException(status_code=404, detail=str(e))