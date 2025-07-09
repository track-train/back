class DomainError(Exception):
    """Racine pour toutes les erreurs métier."""
    pass

class DuplicateProfileError(DomainError):
    """Email déjà utilisé."""
    pass

class ProfileNotFoundError(DomainError):
    """Profil non trouvé."""
    pass

class AuthorizationError(DomainError):
    """Erreur d'autorisation."""
    pass

class TokenExpiredError(DomainError):
    """Jeton expiré."""
    pass

class TokenInvalidError(DomainError):
    """Jeton invalide."""
    pass

class TokenMissingError(DomainError):
    """Jeton manquant."""
    pass
