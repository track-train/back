from passlib.context import CryptContext
from src.domain.ports.password_hasher import PasswordHasher

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BcryptPasswordHasher(PasswordHasher):
    def hash(self, plain: str) -> str:
        return pwd_context.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)