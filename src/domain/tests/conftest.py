import pytest
import pytest_asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
from src.container import Container

@pytest.fixture(scope="session")
def container():
    """Container configuré pour les tests avec repositories inmemory"""
    # Force l'environnement test pour utiliser inmemory
    return Container(env="test")

@pytest.fixture
def profile_service(container):
    """Service Profile avec repository inmemory"""
    return container.get_profile_service()

@pytest.fixture  
def group_service(container):
    """Service Group avec repository inmemory"""
    return container.get_group_service()

# Fixtures pour avoir des données de test propres
@pytest_asyncio.fixture
async def admin_profile(profile_service):
    """Récupère le profil admin pré-créé par le container"""
    profiles = await profile_service.get_all_users()  # Méthode correcte
    admin = next((p for p in profiles if "admin" in p.roles), None)
    return admin  # Cette ligne renvoie bien l'admin ou None si non trouvé
