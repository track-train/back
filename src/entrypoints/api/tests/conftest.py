import pytest
import os
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.container import Container
import pytest_asyncio



# Avant tout, on définit la variable d'environnement
@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ["ENV"] = "test"  # Configure l'environnement à "test"
    yield
    # Optionnel : tu peux aussi réinitialiser la variable d'environnement après les tests si nécessaire


# Fixture pour initialiser un conteneur unique pour tous les tests
@pytest.fixture(scope="module", autouse=True)
def container():
    # Créer un conteneur en mémoire avec ENV='test'
    c = Container(env="test")  # Assure que le conteneur utilise l'environnement 'test'

    # Assurer que le conteneur utilise une base en mémoire
    assert os.getenv("ENV") == "test", "L'environnement n'est pas correctement configuré sur 'test'."
    
    # Retourner le conteneur pour qu'il soit partagé dans tous les tests
    return c


# Fournit un client HTTPX asynchrone monté sur l'ASGI de FastAPI
@pytest_asyncio.fixture
async def client(container):
    """
    Fournit un AsyncClient HTTPX monté sur l'ASGI FastAPI avec un environnement de test.
    """
    transport = ASGITransport(app=app)
    
    # Créer et retourner un client HTTPX pour les tests
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac  # Retourne le client pour les tests
