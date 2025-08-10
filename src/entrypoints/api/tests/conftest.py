import pytest
import os
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.container import Container
import pytest_asyncio



@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ["ENV"] = "test" 
    yield


@pytest.fixture(scope="module", autouse=True)
def container():
    c = Container(env="test")  

    assert os.getenv("ENV") == "test", "L'environnement n'est pas correctement configuré sur 'test'."
    
    return c


@pytest_asyncio.fixture
async def client(container):

    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac 

@pytest.fixture(scope="session")
def test_state():
  
    return {}