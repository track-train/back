class DomainError(Exception):
    """Racine pour toutes les erreurs métier."""
    pass

class InvalidConfirmPasswordError(DomainError):
    """Confirm password does not match."""
    pass

class InvalidFormatEmailError(DomainError):
    """Invalid email format."""
    pass

class DuplicateProfileError(DomainError):
    """Email already used."""
    pass

class NotFoundError(DomainError):
    """Not Found."""
    pass

class AuthorizationError(DomainError):
    """Authorization error."""
    pass

class TokenExpiredError(DomainError):
    """Expired token."""
    pass

class TokenInvalidError(DomainError):
    """Invalid token."""
    pass

class TokenMissingError(DomainError):
    """Missing token."""
    pass

class AuthenticationError(DomainError):
    """Authentification failed."""

class ValidationError(DomainError):
    """Validation error."""
    pass