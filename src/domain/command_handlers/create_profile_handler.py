from uuid import uuid4
from datetime import datetime

from src.domain.commands.create_profile import CreateProfileCommand
from src.domain.ports.profile_repository import ProfileRepository
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.exceptions import DuplicateProfileError
from src.domain.model.profile import Profile as DomainProfile

class CreateProfileHandler:
    def __init__(self, repo: ProfileRepository, hasher: PasswordHasher):
        self._repo = repo
        self._hasher = hasher

    def handle(self, cmd: CreateProfileCommand) -> DomainProfile:
        # Vérifier unicité de l'email
        if self._repo.find_by_email(cmd.email):
            raise DuplicateProfileError(f"Email {cmd.email} déjà utilisé")

        # Hasher le mot de passe
        hashed_pw = self._hasher.hash(cmd.password)
        # Construire l'entité métier
        profile = DomainProfile(
            id=uuid4(),
            email=cmd.email,
            password=hashed_pw,
            name=cmd.name,
            sex=cmd.sex,
            age=cmd.age,
            contact=cmd.contact,
            pricing=cmd.pricing,
            description=cmd.description,
            legacy=cmd.legacy,
            roles=["user"],
            created_at=datetime.utcnow()
        )

        # Persister
        return self._repo.add(profile)