import json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from uuid import UUID
from datetime import date

from src.container import container
from src.entrypoints.api.deps.auth import get_current_user, require_owner_or_admin
from src.entrypoints.api.schemas.daily_checkup import DailyCheckupCreate, DailyCheckupRead
from src.domain.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/daily-checkups", tags=["daily-checkups"])

@router.post("", response_model=DailyCheckupRead, status_code=status.HTTP_201_CREATED)
async def create_daily_checkup(
    sleepduration: Optional[str] = Form(None),
    sleepquality: Optional[int] = Form(None),
    weight: Optional[float] = Form(None),
    shape: Optional[int] = Form(None),
    soreness: Optional[int] = Form(None),
    steps: Optional[int] = Form(None),
    digestion: Optional[int] = Form(None),
    dayon: Optional[bool] = Form(None),
    pictures: List[UploadFile] = File(default=[]),
    user=Depends(get_current_user)
):
    service = container.get_daily_checkup_service()

    try:
        dto = DailyCheckupCreate(
            sleepduration=sleepduration,
            sleepquality=sleepquality,
            weight=weight,
            shape=shape,
            soreness=soreness,
            steps=steps,
            digestion=digestion,
            dayon=dayon
        )

        for file in pictures:
            if file.size and file.size > 2 * 1024 * 1024:
                raise HTTPException(400, f"File {file.filename} too large. Maximum size is 2MB.")

        picture_files = []
        for file in pictures:
            if file.filename:
                picture_files.append((file.file, file.filename))
        
        checkup = await service.create(
            profile_id=UUID(user["sub"]),
            sleepduration=sleepduration,
            sleepquality=sleepquality,
            weight=weight,
            shape=shape,
            soreness=soreness,
            steps=steps,
            digestion=digestion,
            dayon=dayon,
            picture_files=picture_files
        )
        return DailyCheckupRead.model_validate(checkup)
         
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {str(e)}")
    

@router.get("/mine", response_model=List[DailyCheckupRead])
async def get_my_daily_checkups(user=Depends(get_current_user)):
    service = container.get_daily_checkup_service()
    checkups = await service.get_by_profile_id(UUID(user["sub"]))
    return [DailyCheckupRead.model_validate(checkup) for checkup in checkups]

@router.get("/today", response_model=Optional[DailyCheckupRead])
async def get_today_checkup(user=Depends(get_current_user)):
    service = container.get_daily_checkup_service()
    checkup = await service.get_today_checkup(UUID(user["sub"]))
    if checkup:
        return DailyCheckupRead.model_validate(checkup)
    return None

@router.get("/{checkup_id}", response_model=DailyCheckupRead)
async def get_daily_checkup(
    checkup_id: UUID,
    user=Depends(get_current_user)
):
    service = container.get_daily_checkup_service()
    try:
        checkup = await service.get_by_id(checkup_id)
        if str(checkup.profile_id) != user["sub"] and "admin" not in user.get("roles", []):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return DailyCheckupRead.model_validate(checkup)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily checkup not found")

@router.delete("/{checkup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_checkup(
    checkup_id: UUID,
    user=Depends(get_current_user)
):
    service = container.get_daily_checkup_service()
    try:
        checkup = await service.get_by_id(checkup_id)
        if str(checkup.profile_id) != user["sub"] and "admin" not in user.get("roles", []):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        await service.delete(checkup_id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily checkup not found")