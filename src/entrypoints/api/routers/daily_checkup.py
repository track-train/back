from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
from uuid import UUID

from src.entrypoints.api.schemas.daily_checkup import (
    DailyCheckupCreate,
    DailyCheckupResponse,
    DailyCheckupListResponse,
    MessageResponse
)
from src.entrypoints.api.deps.auth import get_current_user
from src.domain.exceptions import NotFoundError
from src.container import container

router = APIRouter(prefix="/daily-checkups", tags=["Daily Checkups"])

@router.post("/", response_model=DailyCheckupResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
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
    """Créer un nouveau daily checkup pour l'utilisateur connecté"""
    service = container.get_daily_checkup_service()
    
    try:
        # Validation des scores (1-10)
        score_fields = {
            "sleepquality": sleepquality,
            "shape": shape,
            "soreness": soreness,
            "digestion": digestion
        }
        
        for field_name, value in score_fields.items():
            if value is not None and (value < 1 or value > 10):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field_name} must be between 1 and 10"
                )
        
        if weight is not None and weight <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Weight must be greater than 0"
            )
        
        if steps is not None and steps < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Steps must be greater than or equal to 0"
            )
        
        picture_files = []
        if pictures:
            for picture in pictures:
                if picture.filename:
                    content = await picture.read()
                    picture_files.append((content, picture.filename))
        
        daily_checkup = await service.create(
            profile_id=UUID(user["sub"]),
            sleepduration=sleepduration,
            sleepquality=sleepquality,
            weight=weight,
            shape=shape,
            soreness=soreness,
            steps=steps,
            digestion=digestion,
            dayon=dayon,
            picture_files=picture_files if picture_files else None
        )
        
        return DailyCheckupResponse.model_validate(daily_checkup)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{checkup_id}", response_model=DailyCheckupResponse, dependencies=[Depends(get_current_user)])
async def get_daily_checkup(
    checkup_id: UUID,
    user=Depends(get_current_user)
):
    """Récupérer un daily checkup spécifique par son ID"""
    service = container.get_daily_checkup_service()
    
    try:
        daily_checkup = await service.get_by_id(checkup_id)
        
        if daily_checkup.profile_id != UUID(user["sub"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this daily checkup"
            )
        
        return DailyCheckupResponse.model_validate(daily_checkup)
        
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily checkup not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/", response_model=DailyCheckupListResponse, dependencies=[Depends(get_current_user)])
async def get_user_daily_checkups(
    user=Depends(get_current_user)
):
    """Récupérer tous les daily checkups de l'utilisateur connecté"""
    service = container.get_daily_checkup_service()
    
    try:
        daily_checkups = await service.get_by_profile_id(UUID(user["sub"]))
        
        return DailyCheckupListResponse(
            daily_checkups=[DailyCheckupResponse.model_validate(dc) for dc in daily_checkups],
            total=len(daily_checkups)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{checkup_id}", response_model=MessageResponse, dependencies=[Depends(get_current_user)])
async def delete_daily_checkup(
    checkup_id: UUID,
    user=Depends(get_current_user)
):
    """Supprimer un daily checkup spécifique"""
    service = container.get_daily_checkup_service()
    
    try:
        daily_checkup = await service.get_by_id(checkup_id)
        
        if daily_checkup.profile_id != UUID(user["sub"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this daily checkup"
            )
        
        await service.delete(checkup_id)
        
        return MessageResponse(message="Daily checkup deleted successfully")
        
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Daily checkup not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )