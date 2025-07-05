class DomainError(Exception):
    """Racine pour toutes les erreurs métier."""
    pass

class DuplicateProfileError(DomainError):
    """Email déjà utilisé."""
    pass

class ProfileNotFoundError(DomainError):
    """Profil non trouvé."""
    pass

