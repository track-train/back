from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from uuid import UUID

from sqlalchemy.sql.functions import user
from starlette.status import HTTP_404_NOT_FOUND


from src.container import container
from src.domain.lib.jwt_manager import create_access_token
from src.entrypoints.api.schemas.profile import EmailUpdate, PasswordUpdate, ProfileCreate, ProfileRead, ProfileWithToken, RolesUpdate, TokenResponse, ProfileLogin, ProfilUpdate, CoachProfileRead
from src.domain.exceptions import DuplicateProfileError, InvalidConfirmPasswordError, InvalidFormatEmailError, NotFoundError, AuthenticationError
from src.entrypoints.api.deps.auth import UserPayload, get_current_user, require_owner_or_admin
from src.entrypoints.api.deps.roles import require_roles


router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.post("", response_model=ProfileWithToken, status_code=status.HTTP_201_CREATED)
async def create_profile(
    dto: ProfileCreate,
):
    service = container.get_profile_service()

    try:
        profile = await service.create(
            email=dto.email,
            raw_password=dto.password,
            confirm_password=dto.confirm_password,
            name=dto.name or "",
            sex=dto.sex,
            age=dto.age,
            contact=dto.contact,
            pricing=dto.pricing,
            description=dto.description,
            legacy=dto.legacy,
        )
    except DuplicateProfileError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidConfirmPasswordError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InvalidFormatEmailError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    token = create_access_token(
        subject=str(profile.id),
        roles=profile.roles,
    )

    profile_dto = ProfileRead.model_validate(profile)
    token_dto = TokenResponse(access_token=token)

    return ProfileWithToken(profile=profile_dto, token=token_dto)

@router.get("/users", response_model= list[ProfileRead], status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles("admin", "coach"))])
async def get_all_user_profiles():
    service = container.get_profile_service()
    try:
        profiles = await service.get_all_users()
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return [ProfileRead.model_validate(profile) for profile in profiles]

@router.get("/coachs", response_model= list[CoachProfileRead], status_code=status.HTTP_200_OK)
async def get_all_coach_profiles():
    service = container.get_profile_service()
    try:
        profiles = await service.get_all_coachs()
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return [CoachProfileRead.model_validate(profile) for profile in profiles]


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    dto: ProfileLogin,
):
    service = container.get_profile_service()
    try:
        profile = await service.login(email=dto.email, password=dto.password)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except InvalidFormatEmailError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        profile = await service.get_by_id(UUID(user["sub"]))
    except NotFoundError:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Profile not found"
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
        updated = await service.update(profile_id, **update_data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return ProfileRead.model_validate(updated)

@router.get("/{profile_id}", response_model=ProfileRead, status_code=status.HTTP_200_OK, dependencies=[Depends(require_roles("admin", "coach"))])
async def get_user_profile(profile_id: UUID):
    service = container.get_profile_service()
    try:
        profile = await service.get_by_id(profile_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ProfileRead.model_validate(profile)

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_owner_or_admin)])
async def delete_profile(
    profile_id: UUID,
): 
    service = container.get_profile_service()
    try: 
        await service.delete(profile_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return None



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
        updated = await service.update_email(profile_id, dto.email)
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
        await service.update_password(
            profile_id,
            old_password=dto.old_password,
            new_password=dto.new_password
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AuthenticationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return None


@router.patch(
    "/{profile_id}/roles",
    response_model=ProfileRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles("admin"))]
)
async def patch_roles(
    profile_id: UUID,
    dto: RolesUpdate,
):
    service = container.get_profile_service()
    try:
        updated = await service.update_roles(profile_id, dto.roles)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return ProfileRead.model_validate(updated)

@router.patch(
        "/profile-picture/{profile_id}",
        response_model=ProfileRead,
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_owner_or_admin)]
)
async def update_my_profile_picture(
    file: UploadFile = File(...),
    user: UserPayload = Depends(get_current_user)
):
    """Update current user's profile picture"""
    if file.size > 2 * 1024 * 1024:  # 2MB limit
        raise HTTPException(400, "File too large. Maximum size is 2MB.")
    
    try:
        user_id = UUID(user["sub"])
        service = container.get_profile_service()
        
        profile = await service.update_profile_picture(user_id, file.file, file.filename)
        return ProfileRead.model_validate(profile)
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@router.patch(
        "/background-picture/{profile_id}",
        response_model=ProfileRead,
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_owner_or_admin)]
)
async def update_my_background_picture(
    file: UploadFile = File(...),
    user: UserPayload = Depends(get_current_user)
):
    """Update current user's background picture"""
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large. Maximum size is 5MB.")
    
    try:
        user_id = UUID(user["sub"])
        service = container.get_profile_service()
        
        profile = await service.update_background_picture(user_id, file.file, file.filename)
        return ProfileRead.model_validate(profile)
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@router.delete(
        "/profile-picture/{profile_id}",
        response_model=ProfileRead,
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_owner_or_admin)]
)
async def delete_my_profile_picture(
    user: UserPayload = Depends(get_current_user)
):
    """Delete current user's profile picture"""
    try:
        user_id = UUID(user["sub"])
        service = container.get_profile_service()
        
        profile = await service.delete_profile_picture(user_id)
        return ProfileRead.model_validate(profile)
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Delete failed: {str(e)}")

@router.delete(
        "/background-picture/{profile_id}",
        response_model=ProfileRead,
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(require_owner_or_admin)]
)
async def delete_my_background_picture(
    user: UserPayload = Depends(get_current_user)
):
    """Delete current user's background picture"""
    try:
        user_id = UUID(user["sub"])
        service = container.get_profile_service()
        
        profile = await service.delete_background_picture(user_id)
        return ProfileRead.model_validate(profile)
        
    except ValueError as e:
        raise HTTPException(400, str(e))
    except NotFoundError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Delete failed: {str(e)}")