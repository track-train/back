from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID


from src.container import container
from src.domain.lib.jwt_manager import create_access_token
from src.entrypoints.api.schemas.profile import ProfileCreate, ProfileRead, ProfileWithToken, TokenResponse, ProfileLogin
from src.domain.exceptions import DuplicateProfileError, NotFoundError, AuthenticationError
from src.entrypoints.api.deps.auth import get_current_user
from src.entrypoints.api.deps.roles import require_roles


router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("", response_model=ProfileWithToken, status_code=status.HTTP_201_CREATED)
async def create_profile(
    dto: ProfileCreate,
):
    service = container.get_profile_service()

    try:
        profile = service.create(
            email=dto.email,
            raw_password=dto.password,
            name=dto.name or "",
            sex=dto.sex,
            age=dto.age,
            contact=dto.contact,
            pricing=dto.pricing,
            description=dto.description,
            legacy=dto.legacy,
        )
    except DuplicateProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    token = create_access_token(
        subject=str(profile.id),
        roles=profile.roles,
    )

    profile_dto = ProfileRead.model_validate(profile)
    token_dto = TokenResponse(access_token=token)

    return ProfileWithToken(profile=profile_dto, token=token_dto)

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_current_user)])
async def delete_profile(
    profile_id: UUID,
): 
    service = container.get_profile_service()
    try: 
        service.delete(profile_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return None

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    dto: ProfileLogin,
):
    service = container.get_profile_service()
    try:
        profile = service.login(email=dto.email, password=dto.password)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    token = create_access_token(
        subject=str(profile.id),
        roles=profile.roles,
    )
    return TokenResponse(access_token=token)
