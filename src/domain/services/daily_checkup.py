from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, date
import os
from src.domain.model.daily_checkup import DailyCheckup
from src.domain.ports.daily_checkup_repository import DailyCheckupRepository
from src.domain.ports.image_storage import DailyCheckupImageType, ImageStorage
from src.domain.exceptions import NotFoundError, ValidationError


class DailyCheckupService:
    def __init__(self, repository: DailyCheckupRepository, image_storage: ImageStorage):
        self._repo = repository
        self._image_storage = image_storage

    def _generate_image_filename(self, original_filename: str, profile_id: UUID, index: int) -> str:
        """Generate unique filename for daily checkup images"""
        _, ext = os.path.splitext(original_filename)
        if not ext:
            ext = '.jpg'
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        
        return f"daily_checkups/{profile_id}/{timestamp}_{index}_{unique_id}{ext}"
        
    def _validate_image_file(self, filename: str) -> bool:
        """Validate if file is an allowed image type"""
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        _, ext = os.path.splitext(filename.lower())
        return ext in allowed_extensions

    async def create(
        self,
        profile_id: UUID,
        sleepduration: Optional[str] = None,
        sleepquality: Optional[int] = None,
        weight: Optional[float] = None,
        shape: Optional[int] = None,
        soreness: Optional[int] = None,
        steps: Optional[int] = None,
        digestion: Optional[int] = None,
        dayon: Optional[bool] = None,
        picture_files: Optional[List[tuple]] = None
    ) -> DailyCheckup:
        
        today = date.today()
        existing = await self._repo.find_by_profile_id_and_date(profile_id, today)
        if existing:
            raise ValidationError(f"Daily checkup already exists for today")

        picture_urls = []
        if picture_files:
            for i, (file_data, filename) in enumerate(picture_files):
                if not self._validate_image_file(filename):
                    raise ValueError(f"Invalid file type for {filename}. Only JPG, JPEG, PNG, and WebP are allowed.")

                new_filename = self._generate_image_filename(filename, profile_id, DailyCheckupImageType.DAILY_CHECKUP)
                url = await self._image_storage.upload(file_data, new_filename, DailyCheckupImageType.DAILY_CHECKUP)
                picture_urls.append(url)

        daily_checkup = DailyCheckup(
            id=uuid4(),
            profile_id=profile_id,
            sleepduration=sleepduration,
            sleepquality=sleepquality,
            weight=weight,
            shape=shape,
            soreness=soreness,
            steps=steps,
            digestion=digestion,
            dayon=dayon,
            picture=picture_urls,
            created_at=datetime.utcnow() 
        )


        daily_checkup._validate_score_fields()

        return await self._repo.add(daily_checkup)

    async def get_by_id(self, checkup_id: UUID) -> DailyCheckup:
        """Récupère un daily checkup par son ID"""
        checkup = await self._repo.find_by_id(checkup_id)
        if not checkup:
            raise NotFoundError(f"Daily checkup {checkup_id} not found")
        return checkup

    async def get_by_profile_id(self, profile_id: UUID) -> List[DailyCheckup]:
        """Récupère tous les daily checkups d'un profil"""
        return await self._repo.find_by_profile_id(profile_id)

    async def get_by_profile_and_date(self, profile_id: UUID, target_date: date) -> Optional[DailyCheckup]:
        """Récupère un daily checkup par profil et date (via created_at)"""
        return await self._repo.find_by_profile_id_and_date(profile_id, target_date)

    async def get_today_checkup(self, profile_id: UUID) -> Optional[DailyCheckup]:
        """Récupère le checkup d'aujourd'hui pour un utilisateur"""
        today = date.today()
        return await self._repo.find_by_profile_id_and_date(profile_id, today)

    async def delete(self, checkup_id: UUID) -> None:
        """Supprime un daily checkup"""
        existing = await self.get_by_id(checkup_id)

        if existing.picture:
            for picture_url in existing.picture:
                try:
                    old_key = self._image_storage.extract_key_from_url(picture_url)
                    await self._image_storage.delete(old_key)
                except Exception:
                    pass
        
        await self._repo.delete(checkup_id)

    async def add_pictures(self, checkup_id: UUID, picture_files: List[tuple]) -> DailyCheckup:
        """Ajoute des images à un daily checkup existant"""
        existing = await self.get_by_id(checkup_id)
        
        picture_urls = existing.picture.copy()
        
        for i, (file_data, filename) in enumerate(picture_files):
            if not self._validate_image_file(filename):
                raise ValueError(f"Invalid file type for {filename}. Only JPG, JPEG, PNG, and WebP are allowed.")
            
            new_filename = self._generate_image_filename(filename, existing.profile_id, len(picture_urls) + i)
            url = await self._image_storage.upload(file_data, new_filename)
            picture_urls.append(url)

        existing.picture = picture_urls

        return await self._repo.update(existing)

    async def remove_picture(self, checkup_id: UUID, picture_url: str) -> DailyCheckup:
        """Supprime une image spécifique d'un daily checkup"""
        existing = await self.get_by_id(checkup_id)
        
        if picture_url not in existing.picture:
            raise ValueError(f"Picture {picture_url} not found in checkup")
        
        try:
            old_key = self._image_storage.extract_key_from_url(picture_url)
            await self._image_storage.delete(old_key)
        except Exception:
            pass

        existing.picture = [url for url in existing.picture if url != picture_url]

        return await self._repo.update(existing)