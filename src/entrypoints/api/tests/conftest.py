import pytest
import os
from uuid import uuid4

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.container import Container
from src.domain.model.profile import Profile as DomainProfile
from src.domain.model.group   import Group   as DomainGroup

@pytest.fixture(autouse=True)
def seed_data(monkeypatch):
    # 1) Forcer ENV=test et container unique
    monkeypatch.setenv("ENV", "test")
    c = Container(env="test")
    monkeypatch.setattr("src.container.container", c)

    # helper pour créer et seed des profils
    def _mk(email: str, pw: str, roles: list[str]):
        h = c.hasher.hash(pw)
        p = DomainProfile(
            id=uuid4(), email=email, password=h,
            name=email.split("@")[0], sex=None, age=None,
            contact=None, pricing=None, description=None,
            legacy=False, roles=roles, created_at=None
        )
        c.profile_repo.add(p)
        return p, pw

    admin = _mk("admin@example.com",  "AdminPass123!", ["admin"])
    coach = _mk("coach@example.com", "CoachPass123!", ["coach"])
    user  = _mk("user@example.com",  "UserPass123!",  ["user"])

    # Seed un groupe pour le coach
    grp = DomainGroup(
        id=uuid4(),
        owner_id=coach[0].id,
        name="GroupeTest",
        description="Pour tests",
        created_at=None
    )
    c.group_repo.add(grp)

    return {
        "container": c,
        "admin":     admin,
        "coach":     coach,
        "user":      user,
        "group":     grp,
    }

@pytest_asyncio.fixture
async def client():
    """
    Fournit un AsyncClient HTTPX monté sur l'ASGI FastAPI.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
