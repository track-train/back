from src.domain.commands.delete_profile import DeleteProfileCommand
from src.domain.ports.profile_repository import ProfileRepository
from src.domain.exceptions import ProfileNotFoundError

class DeleteProfileHandler:
    def __init__(self, repo: ProfileRepository):
        self._repo = repo

    def handle(self, cmd: DeleteProfileCommand) -> None:
        # 1. Vérifier l’existence
        if not self._repo.find_by_id(cmd.id):
            raise ProfileNotFoundError(f"Profil {cmd.id} introuvable")

        # 2. Supprimer
        self._repo.delete(cmd.id)
