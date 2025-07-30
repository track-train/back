from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

from src.domain.model.profile import Profile as DomainProfile
from src.domain.ports.profile_repository import ProfileRepository
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.exceptions import DuplicateProfileError, AuthenticationError, NotFoundError, InvalidConfirmPasswordError, InvalidFormatEmailError
import re

class ProfileService:
    def __init__(self, repo: ProfileRepository, hasher: PasswordHasher):
        self._repo = repo
        self._hasher = hasher


    def create(self,
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

        if self._repo.find_by_email(email):
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
        
        return  self._repo.add(profile)
    
    def delete(self, profile_id: UUID):
        profile = self._repo.find_by_id(profile_id)
        if not profile:
            raise NotFoundError(f"Profile with id {profile_id} not found")
        
        
        self._repo.delete(profile_id)

    def login(self, email: str, password: str) -> DomainProfile:
        profile = self._repo.find_by_email(email)

        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            raise InvalidFormatEmailError(f"Email {email} has invalid format")

        if not profile:
            raise AuthenticationError(f"Invalid password or email")
        
        if not self._hasher.verify(password, profile.password):
            raise AuthenticationError(f"Invalid password or email")
        
        return profile
    
    def get_by_id(self, profile_id: UUID) -> DomainProfile:
        profile = self._repo.find_by_id(profile_id)
        if not profile:
            raise NotFoundError(f"Profile with id {profile_id} not found")
        
        return profile

    def get_all_users(self) -> List[DomainProfile]:
        profiles = self._repo.find_all_users()
        if not profiles:
            raise NotFoundError("No profiles found")
        
        return profiles
    
    def get_all_coachs(self) -> List[DomainProfile]:
        profiles = self._repo.find_all_coachs()
        if not profiles:
            raise NotFoundError("No profiles found")
        
        return profiles
    
    def update(self,
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
        profile = self.get_by_id(id)  

        for attr, val in {
            "name": name, "sex": sex, "age": age,
            "contact": contact, "pricing": pricing,
            "description": description, "legacy": legacy,
            "roles": roles
        }.items():
            if val is not None:
                setattr(profile, attr, val)

        return self._repo.update(profile)
    
    def update_email(self, id: UUID, new_email: str) -> DomainProfile:
        profile = self.get_by_id(id)  
        if new_email != profile.email and self._repo.find_by_email(new_email):
            raise DuplicateProfileError(f"Email {new_email} already use")
        profile.email = new_email
        return self._repo.update(profile)

    def update_password(self, id: UUID, old_password: str, new_password: str) -> None:
        profile = self.get_by_id(id) 
        if not self._hasher.verify(old_password, profile.password):
            raise AuthenticationError("Wrong password")
        profile.password = self._hasher.hash(new_password)
        self._repo.update(profile)
    
    def update_roles(self, id: UUID, roles: List[str]) -> DomainProfile:
        profile = self.get_by_id(id)  
        if not roles:
            raise ValueError("Roles cannot be empty")
        profile.roles = roles
        return self._repo.update(profile)
