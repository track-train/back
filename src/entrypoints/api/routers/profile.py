from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from sqlalchemy.sql.functions import user
from starlette.status import HTTP_404_NOT_FOUND


from src.container import container
from src.domain.lib.jwt_manager import create_access_token
from src.entrypoints.api.schemas.profile import EmailUpdate, PasswordUpdate, ProfileCreate, ProfileRead, ProfileWithToken, TokenResponse, ProfileLogin, ProfilUpdate
from src.domain.exceptions import DuplicateProfileError, NotFoundError, AuthenticationError
from src.entrypoints.api.deps.auth import UserPayload, get_current_user, require_owner_or_admin
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

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_owner_or_admin)])
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

@router.get("/me", response_model=ProfileRead)
async def get_me(
    user: UserPayload = Depends(get_current_user),
):

    try:
        profile_id = UUID(user["sub"])
    except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user id"
            )
    service = container.get_profile_service()
    
    try:
        profile = service.get_by_id(UUID(user["sub"]))
    except NotFoundError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Profil not found"
        ) 

    return ProfileRead.model_validate(profile)

@router.patch("/{profile_id}", response_model=ProfileRead, status_code=status.HTTP_200_OK, dependencies=[Depends(require_owner_or_admin)])
async def patch_profile(
    profile_id: UUID,
    dto: ProfilUpdate,

):
    service = container.get_profile_service()

    update_data = dto.model_dump(exclude_none=True, by_alias=True)

    try:
        updated = service.update(profile_id, **update_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return ProfileRead.model_validate(updated)


@router.patch(
    "/{profile_id}/email",
    response_model=ProfileRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_owner_or_admin)]
)
async def patch_email(
    profile_id: UUID,
    dto: EmailUpdate,
):
    service = container.get_profile_service()
    try:
        updated = service.update_email(profile_id, dto.email)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DuplicateProfileError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ProfileRead.model_validate(updated)


@router.patch(
    "/{profile_id}/password",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_owner_or_admin)]
)
async def patch_password(
    profile_id: UUID,
    dto: PasswordUpdate,
):
    service = container.get_profile_service()
    try:
        service.update_password(
            profile_id,
            old_password=dto.old_password,
            new_password=dto.new_password
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return None
