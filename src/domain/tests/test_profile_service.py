import pytest
from uuid import uuid4
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.domain.services.profile import ProfileService
from src.domain.ports.profile_repository import ProfileRepository
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.exceptions import DuplicateProfileError, AuthenticationError, NotFoundError, InvalidConfirmPasswordError, InvalidFormatEmailError
from unittest.mock import AsyncMock


# Fixture pour simuler le repository (ProfileRepository)
@pytest.fixture
def mock_repo():
    repo = AsyncMock(spec=ProfileRepository)
    return repo


# Fixture pour simuler le PasswordHasher
@pytest.fixture
def mock_hasher():
    hasher = AsyncMock(spec=PasswordHasher)
    return hasher


# Fixture pour simuler l'ImageStorage
@pytest.fixture
def mock_image_storage():
    storage = AsyncMock()
    return storage


# Fixture pour créer une instance de ProfileService avec les mocks
@pytest.fixture
def profile_service(mock_repo, mock_hasher, mock_image_storage):
    return ProfileService(repo=mock_repo, hasher=mock_hasher, image_storage=mock_image_storage)


# Test de la création de profil avec email déjà existant
@pytest.mark.asyncio
async def test_create_profile_duplicate_email(profile_service, mock_repo):
    email = "test@example.com"
    password = "password123"
    confirm_password = "password123"
    
    # Simuler qu'un profil existe déjà avec l'email
    mock_repo.find_by_email.return_value = object()
    with pytest.raises(DuplicateProfileError):
        await profile_service.create(
            email=email,
            raw_password=password,
            confirm_password=confirm_password
        )


# Test de la création de profil avec un format d'email invalide
@pytest.mark.asyncio
async def test_create_profile_invalid_email(profile_service):
    email = "invalidemail"
    password = "password123"
    confirm_password = "password123"

    with pytest.raises(InvalidFormatEmailError):
        await profile_service.create(
            email=email,
            raw_password=password,
            confirm_password=confirm_password
        )


# Test de la création de profil avec des mots de passe non correspondants
@pytest.mark.asyncio
async def test_create_profile_password_mismatch(profile_service, mock_repo):
    email = "test@example.com"
    password = "password123"
    confirm_password = "differentpassword"
    
    # Simuler qu'aucun profil n'existe avec cet email (None au lieu d'un objet)
    mock_repo.find_by_email.return_value = None

    with pytest.raises(InvalidConfirmPasswordError):
        await profile_service.create(
            email=email,
            raw_password=password,
            confirm_password=confirm_password
        )


# Test de la suppression de profil avec ID existant
@pytest.mark.asyncio
async def test_delete_profile_success(profile_service, mock_repo):
    profile_id = uuid4()
    
    # Simuler qu'un profil existe
    profile = AsyncMock()
    profile.id = profile_id
    mock_repo.find_by_id.return_value = profile
    await profile_service.delete(profile_id)

    mock_repo.find_by_id.assert_called_once_with(profile_id)
    mock_repo.delete.assert_called_once_with(profile_id)


# Test de la suppression de profil avec ID non existant
@pytest.mark.asyncio
async def test_delete_profile_not_found(profile_service, mock_repo):
    profile_id = uuid4()
    
    # Simuler qu'aucun profil n'est trouvé
    mock_repo.find_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await profile_service.delete(profile_id)


# Test de login avec succès
@pytest.mark.asyncio
async def test_login_success(profile_service, mock_repo, mock_hasher):
    email = "test@example.com"
    password = "password123"
    
    profile = AsyncMock()
    profile.email = email
    profile.password = "hashedpassword"
    mock_repo.find_by_email.return_value = profile
    mock_hasher.verify.return_value = True

    logged_in_profile = await profile_service.login(email=email, password=password)

    mock_repo.find_by_email.assert_called_once_with(email)
    mock_hasher.verify.assert_called_once_with(password, profile.password)

    assert logged_in_profile == profile


# Test de login avec mot de passe incorrect
@pytest.mark.asyncio
async def test_login_invalid_password(profile_service, mock_repo, mock_hasher):
    email = "test@example.com"
    password = "wrongpassword"
    
    profile = AsyncMock()
    profile.email = email
    profile.password = "hashedpassword"
    mock_repo.find_by_email.return_value = profile
    mock_hasher.verify.return_value = False

    with pytest.raises(AuthenticationError):
        await profile_service.login(email=email, password=password)


# Test de la mise à jour du profil
@pytest.mark.asyncio
async def test_update_profile(profile_service, mock_repo):
    profile_id = uuid4()
    updated_name = "New Name"
    
    # Simuler un profil existant
    profile = AsyncMock()
    profile.id = profile_id
    profile.name = "Old Name"
    mock_repo.find_by_id.return_value = profile
    # Le mock doit retourner le profil modifié, pas un nouveau mock
    mock_repo.update.return_value = profile

    updated_profile = await profile_service.update(
        id=profile_id, name=updated_name
    )

    mock_repo.find_by_id.assert_called_once_with(profile_id)
    mock_repo.update.assert_called_once_with(profile)
    # Vérifier que le nom a été mis à jour sur le profil original
    assert profile.name == updated_name
    assert updated_profile == profile


# Test de mise à jour de l'email
@pytest.mark.asyncio
async def test_update_email(profile_service, mock_repo):
    profile_id = uuid4()
    new_email = "newemail@example.com"
    
    # Simuler un profil existant avec un email
    profile = AsyncMock()
    profile.email = "oldemail@example.com"
    mock_repo.find_by_email.return_value = None  # Simuler qu'aucun autre profil n'a cet email
    mock_repo.find_by_id.return_value = profile
    # Le mock doit retourner le profil modifié
    mock_repo.update.return_value = profile

    updated_profile = await profile_service.update_email(profile_id, new_email)

    mock_repo.find_by_id.assert_called_once_with(profile_id)
    mock_repo.find_by_email.assert_called_once_with(new_email)
    mock_repo.update.assert_called_once_with(profile)
    # Vérifier que l'email a été mis à jour sur le profil original
    assert profile.email == new_email
    assert updated_profile == profile


# Test de mise à jour du mot de passe
@pytest.mark.asyncio
async def test_update_password(profile_service, mock_repo, mock_hasher):
    profile_id = uuid4()
    old_password = "oldpassword"
    new_password = "newpassword"
    
    # Simuler un profil avec un mot de passe
    profile = AsyncMock()
    profile.password = "hashedoldpassword"
    mock_repo.find_by_id.return_value = profile
    mock_hasher.verify.return_value = True
    mock_hasher.hash.return_value = "hashednewpassword"

    await profile_service.update_password(profile_id, old_password, new_password)

    # Corriger l'assertion : vérifier avec l'ancien mot de passe hashé
    mock_hasher.verify.assert_called_once_with(old_password, "hashedoldpassword")
    mock_hasher.hash.assert_called_once_with(new_password)
    mock_repo.update.assert_called_once_with(profile)


# Test de mise à jour des rôles
@pytest.mark.asyncio
async def test_update_roles(profile_service, mock_repo):
    profile_id = uuid4()
    new_roles = ["admin"]
    
    # Simuler un profil avec des rôles existants
    profile = AsyncMock()
    profile.roles = ["user"]
    mock_repo.find_by_id.return_value = profile
    # Le mock doit retourner le profil modifié
    mock_repo.update.return_value = profile

    updated_profile = await profile_service.update_roles(profile_id, new_roles)

    mock_repo.find_by_id.assert_called_once_with(profile_id)
    mock_repo.update.assert_called_once_with(profile)
    # Vérifier que les rôles ont été mis à jour sur le profil original
    assert profile.roles == new_roles
    assert updated_profile == profile


# Tests pour les nouvelles méthodes de gestion d'images
@pytest.mark.asyncio
async def test_update_profile_picture(profile_service, mock_repo, mock_image_storage):
    profile_id = uuid4()
    file_content = b"fake_image_content"
    filename = "profile.jpg"
    
    # Simuler un profil existant
    profile = AsyncMock()
    profile.id = profile_id
    mock_repo.find_by_id.return_value = profile
    mock_repo.update.return_value = profile
    mock_image_storage.upload.return_value = "http://example.com/profile.jpg"

    updated_profile = await profile_service.update_profile_picture(profile_id, file_content, filename)

    mock_repo.find_by_id.assert_called_once_with(profile_id)
    mock_image_storage.upload.assert_called_once()
    mock_repo.update.assert_called_once_with(profile)
    assert updated_profile == profile


@pytest.mark.asyncio
async def test_update_background_picture(profile_service, mock_repo, mock_image_storage):
    profile_id = uuid4()
    file_content = b"fake_image_content"
    filename = "background.jpg"
    
    # Simuler un profil existant
    profile = AsyncMock()
    profile.id = profile_id
    mock_repo.find_by_id.return_value = profile
    mock_repo.update.return_value = profile
    mock_image_storage.upload.return_value = "http://example.com/background.jpg"

    updated_profile = await profile_service.update_background_picture(profile_id, file_content, filename)

    mock_repo.find_by_id.assert_called_once_with(profile_id)
    mock_image_storage.upload.assert_called_once()
    mock_repo.update.assert_called_once_with(profile)
    assert updated_profile == profile


@pytest.mark.asyncio
async def test_delete_profile_picture(profile_service, mock_repo, mock_image_storage):
    profile_id = uuid4()
    
    # Simuler un profil existant avec une photo
    profile = AsyncMock()
    profile.id = profile_id
    profile.profile_picture_url = "http://example.com/profile.jpg"
    mock_repo.find_by_id.return_value = profile
    mock_repo.update.return_value = profile

    updated_profile = await profile_service.delete_profile_picture(profile_id)

    mock_repo.find_by_id.assert_called_once_with(profile_id)
    mock_image_storage.delete.assert_called_once()
    mock_repo.update.assert_called_once_with(profile)
    assert updated_profile == profile


@pytest.mark.asyncio
async def test_delete_background_picture(profile_service, mock_repo, mock_image_storage):
    profile_id = uuid4()
    
    # Simuler un profil existant avec une image de fond
    profile = AsyncMock()
    profile.id = profile_id
    profile.background_picture_url = "http://example.com/background.jpg"
    mock_repo.find_by_id.return_value = profile
    mock_repo.update.return_value = profile

    updated_profile = await profile_service.delete_background_picture(profile_id)

    mock_repo.find_by_id.assert_called_once_with(profile_id)
    mock_image_storage.delete.assert_called_once()
    mock_repo.update.assert_called_once_with(profile)
    assert updated_profile == profile