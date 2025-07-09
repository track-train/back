from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

from src.domain.model.profile import Profile as DomainProfile
from src.domain.ports.profile_repository import ProfileRepository
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.exceptions import DuplicateProfileError, ProfileNotFoundError

class ProfileService:
    def __init__(self, repo: ProfileRepository, hasher: PasswordHasher):
        self._repo = repo
        self._hasher = hasher


    def create(self,
               *,
               email: str,
               raw_password: str,
               name: str,
               sex: Optional[str] = None,
               age: Optional[int] = None,
               contact: Optional[str] = None,
               pricing: Optional[float] = None,
               description: Optional[str] = None,
               legacy: Optional[str] = None,
               roles: Optional[List[str]] = None
               ) -> DomainProfile:
        if self._repo.find_by_email(email):
            raise DuplicateProfileError(f"Profile with email {email} already exists")

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
            # rôle par défaut si non fourni
            roles=roles or ["user"],
            created_at=datetime.utcnow()
        )
        
        return  self._repo.add(profile)
    
    def delete(self, profile_id: UUID):
        profile = self._repo.find_by_id(profile_id)
        if not profile:
            raise ProfileNotFoundError(f"Profile with id {profile_id} not found")
        
        self._repo.delete(profile_id)