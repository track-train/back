from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional, BinaryIO
import os

from src.domain.model.profile import Profile as DomainProfile
from src.domain.ports.profile_repository import ProfileRepository
from src.domain.ports.image_storage import ImageStorage, ProfileImageType   
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.exceptions import DuplicateProfileError, AuthenticationError, NotFoundError, InvalidConfirmPasswordError, InvalidFormatEmailError
import re

class ProfileService:
    def __init__(self, repo: ProfileRepository, hasher: PasswordHasher, image_storage: ImageStorage):
        self._repo = repo
        self._hasher = hasher
        self._image_storage = image_storage


    async def create(self,
               *,
               email: str,
               raw_password: str,
               confirm_password: str,
               name: Optional[str] = None,
               sex: Optional[str] = None,
               age: Optional[int] = None,
               contact: Optional[str] = None,
               pricing: Optional[float] = None,
               description: Optional[str] = None,
               legacy: Optional[str] = None,
               roles: Optional[List[str]] = None
               ) -> DomainProfile:
        
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            raise InvalidFormatEmailError(f"Email {email} has invalid format")

        if await self._repo.find_by_email(email):
            raise DuplicateProfileError(f"Profile with email {email} already exists")
        
        if raw_password != confirm_password:
            raise InvalidConfirmPasswordError("Passwords do not match")

        hashed = self._hasher.hash(raw_password)

        profile = DomainProfile(
            id=uuid4(),
            email=email,
            password=hashed,
            name=name,
            sex=sex,
            age=age,
            contact=contact,
            pricing=pricing,
            description=description,
            legacy=legacy,
            roles=roles or ["user"],
            created_at=datetime.utcnow()
        )
        
        return  await self._repo.add(profile)
    
    async def delete(self, profile_id: UUID):
        profile = await self._repo.find_by_id(profile_id)
        if not profile:
            raise NotFoundError(f"Profile with id {profile_id} not found")
        
        
        await self._repo.delete(profile_id)

    async def login(self, email: str, password: str) -> DomainProfile:
        profile = await self._repo.find_by_email(email)

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            raise InvalidFormatEmailError(f"Email {email} has invalid format")

        if not profile:
            raise AuthenticationError(f"Invalid password or email")
        
        if not self._hasher.verify(password, profile.password):
            raise AuthenticationError(f"Invalid password or email")
        
        return profile
    
    async def get_by_id(self, profile_id: UUID) -> DomainProfile:
        profile = await self._repo.find_by_id(profile_id)
        if not profile:
            raise NotFoundError(f"Profile with id {profile_id} not found")
        
        return profile

    async def get_all_users(self) -> List[DomainProfile]:
        profiles = await self._repo.find_all_users()
        if not profiles:
            raise NotFoundError("No profiles found")
        
        return profiles
    
    async def get_all_coachs(self) -> List[DomainProfile]:
        profiles = await self._repo.find_all_coachs()
        if not profiles:
            raise NotFoundError("No profiles found")
        
        return profiles
    
    async def update(self,
               id: UUID,
               *,
               name: Optional[str] = None,
               sex: Optional[str] = None,
               age: Optional[int] = None,
               contact: Optional[str] = None,
               pricing: Optional[float] = None,
               description: Optional[str] = None,
               legacy: Optional[str] = None,
               roles: Optional[List[str]] = None
               ) -> DomainProfile:
        profile = await self.get_by_id(id)  

        for attr, val in {
            "name": name, "sex": sex, "age": age,
            "contact": contact, "pricing": pricing,
            "description": description, "legacy": legacy,
            "roles": roles
        }.items():
            if val is not None:
                setattr(profile, attr, val)

        return await self._repo.update(profile)
    
    async def update_email(self, id: UUID, new_email: str) -> DomainProfile:
        profile = await self.get_by_id(id)  
        if new_email != profile.email and await self._repo.find_by_email(new_email):
            raise DuplicateProfileError(f"Email {new_email} already use")
        profile.email = new_email
        return await self._repo.update(profile)

    async def update_password(self, id: UUID, old_password: str, new_password: str) -> None:
        profile = await self.get_by_id(id) 
        if not self._hasher.verify(old_password, profile.password):
            raise AuthenticationError("Wrong password")
        profile.password = self._hasher.hash(new_password)
        await self._repo.update(profile)
    
    async def update_roles(self, id: UUID, roles: List[str]) -> DomainProfile:
        profile = await self.get_by_id(id)  
        if not roles:
            raise ValueError("Roles cannot be empty")
        profile.roles = roles
        return await self._repo.update(profile)
    
    def _generate_image_filename(self, original_filename: str, user_id: UUID, image_type: ProfileImageType) -> str:
        """Generate unique filename for profile images"""
        _, ext = os.path.splitext(original_filename)
        if not ext:
            ext = '.jpg'
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid4())[:8]
        
        if image_type == ProfileImageType.PROFILE_PICTURE:
            return f"users/{user_id}/profile/{timestamp}_{unique_id}{ext}"
        else:
            return f"users/{user_id}/background/{timestamp}_{unique_id}{ext}"
        
    def _validate_image_file(self, filename: str) -> bool:
        """Validate if file is an allowed image type"""
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        _, ext = os.path.splitext(filename.lower())
        return ext in allowed_extensions

    async def update_profile_picture(self, user_id: UUID, file: BinaryIO, filename: str) -> DomainProfile:
        """Update user's profile picture"""
        # 1. Récupère le profil (DomainProfile)
        profile = await self.get_by_id(user_id)
        if not profile:
            raise NotFoundError(f"Profile with id {user_id} not found")
        
        # 2. Vérifie le type d'image
        if not self._validate_image_file(filename):
            raise ValueError("Invalid file type. Only JPG, PNG, and WebP are allowed.")
        
        # 3. Supprime l'ancienne image si existante
        if profile.profile_picture_url:
            try:
                old_key = self._image_storage.extract_key_from_url(profile.profile_picture_url)
                await self._image_storage.delete(old_key)
            except Exception:
                pass
        
        # 4. Upload la nouvelle image
        new_filename = self._generate_image_filename(filename, user_id, ProfileImageType.PROFILE_PICTURE)
        new_url = await self._image_storage.upload(file, new_filename, ProfileImageType.PROFILE_PICTURE)
        
        # 5. Mets à jour le champ DomainProfile
        profile.profile_picture_url = new_url
        
        # 6. Passe à la repo pour écriture en BDD (le mapping Domain→ORM→DB doit être correct !)
        return await self._repo.update(profile)
    
    async def update_background_picture(self, user_id: UUID, file: BinaryIO, filename: str) -> DomainProfile:
        """Update user's background picture"""
        profile = await self._repo.find_by_id(user_id)
        if not profile:
            raise NotFoundError(f"Profile with id {user_id} not found")
        
        if not self._validate_image_file(filename):
            raise ValueError("Invalid file type. Only JPG, PNG, and WebP are allowed.")
        
        if profile.background_picture_url:
            try:
                old_key = self._image_storage.extract_key_from_url(profile.background_picture_url)
                await self._image_storage.delete(old_key)
            except Exception:
                pass
        
        new_filename = self._generate_image_filename(filename, user_id, ProfileImageType.BACKGROUND_PICTURE)
        new_url = await self._image_storage.upload(file, new_filename, ProfileImageType.BACKGROUND_PICTURE)
        
        profile.background_picture_url = new_url
        
        return await self._repo.update(profile)

    async def delete_profile_picture(self, user_id: UUID) -> DomainProfile:
        """Delete user's profile picture"""
        profile = await self._repo.find_by_id(user_id)
        if not profile:
            raise NotFoundError(f"Profile with id {user_id} not found")
        
        if not profile.profile_picture_url:
            raise ValueError("No profile picture to delete")
        
        old_key = self._image_storage.extract_key_from_url(profile.profile_picture_url)
        await self._image_storage.delete(old_key)
        
        profile.profile_picture_url = None
        
        return await self._repo.update(profile)

    async def delete_background_picture(self, user_id: UUID) -> DomainProfile:
        profile = await self._repo.find_by_id(user_id)
        if not profile:
            raise NotFoundError(f"Profile with id {user_id} not found")
        
        if not profile.background_picture_url:
            raise ValueError("No background picture to delete")
        
        old_key = self._image_storage.extract_key_from_url(profile.background_picture_url)
        await self._image_storage.delete(old_key)
        
        profile.background_picture_url = None
        
        return await self._repo.update(profile)
    
    