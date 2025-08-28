# src/domain/tests/test_services/test_profile_service.py
import pytest
from uuid import uuid4
from src.domain.exceptions import (
    NotFoundError, 
    DuplicateProfileError, 
    InvalidFormatEmailError,
    AuthenticationError,
    InvalidConfirmPasswordError
)

class TestProfileService:
    
    @pytest.mark.asyncio
    async def test_create_profile_success(self, profile_service):
        """Test création d'un profil valide"""
        # Given
        email = "test@example.com"
        raw_password = "password123"  # Paramètre correct
        name = "Test User"
        
        # When
        profile = await profile_service.create(
            email=email,
            raw_password=raw_password,  # Nom correct
            confirm_password=raw_password,  # Nom correct
            name=name
        )
        
        # Then
        assert profile.email == email
        assert profile.name == name
        assert profile.id is not None
        assert "user" in profile.roles
        assert profile.password != raw_password  # Mot de passe hashé
    
    @pytest.mark.asyncio
    async def test_create_profile_duplicate_email(self, profile_service, admin_profile):
        """Test erreur email déjà utilisé"""
        admin_profile_resolved = await admin_profile  # Attente de la coroutine
        if admin_profile_resolved is None:
         pytest.fail("Admin profile not found!")
        admin_email = admin_profile_resolved.email

        with pytest.raises(DuplicateProfileError):
            await profile_service.create(
                email=admin_email,
                raw_password="password123",
                confirm_password="password123",
                name="Another User"
            )
        
    @pytest.mark.asyncio
    async def test_create_profile_invalid_email(self, profile_service):
        """Test erreur format email invalide"""
        # When/Then
        with pytest.raises(InvalidFormatEmailError):
            await profile_service.create(
                email="invalid-email",  # Format invalide
                raw_password="password123",
                confirm_password="password123",
                name="Test User"
            )
    
    @pytest.mark.asyncio
    async def test_create_profile_passwords_dont_match(self, profile_service):
        """Test erreur mots de passe différents"""
        # When/Then
        with pytest.raises(InvalidConfirmPasswordError):
            await profile_service.create(
                email="test@example.com",
                raw_password="password123",
                confirm_password="different_password",  # Différent
                name="Test User"
            )
    
    @pytest.mark.asyncio
    async def test_login_success(self, profile_service):
        """Test connexion réussie"""
        # Given - Créer un utilisateur
        email = "login@example.com"
        password = "password123"
        await profile_service.create(
            email=email,
            raw_password=password,
            confirm_password=password,
            name="Login User"
        )
        
        # When
        authenticated_profile = await profile_service.login(email, password)
        
        # Then
        assert authenticated_profile.email == email
        assert authenticated_profile.name == "Login User"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, profile_service, admin_profile):
        """Test connexion avec mauvais mot de passe"""
        # When/Then
        with pytest.raises(AuthenticationError):
            await profile_service.login(
                admin_profile.email, 
                "wrong_password"
            )
    
    @pytest.mark.asyncio
    async def test_login_user_not_found(self, profile_service):
        """Test connexion avec utilisateur inexistant"""
        # When/Then
        with pytest.raises(AuthenticationError):
            await profile_service.login(
                "nonexistent@example.com", 
                "password123"
            )
    
    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, profile_service):
        """Test connexion avec email invalide"""
        # When/Then
        with pytest.raises(InvalidFormatEmailError):
            await profile_service.login(
                "invalid-email", 
                "password123"
            )
    
    @pytest.mark.asyncio
    async def test_get_profile_by_id_success(self, profile_service, admin_profile):
        """Test récupération d'un profil par ID"""
        # When
        profile = await profile_service.get_by_id(admin_profile.id)
        
        # Then
        assert profile.id == admin_profile.id
        assert profile.email == admin_profile.email
    
    @pytest.mark.asyncio
    async def test_get_profile_by_id_not_found(self, profile_service):
        """Test récupération d'un profil inexistant"""
        # Given
        non_existent_id = uuid4()
        
        # When/Then
        with pytest.raises(NotFoundError):
            await profile_service.get_by_id(non_existent_id)
    
    @pytest.mark.asyncio
    async def test_update_profile_success(self, profile_service, admin_profile):
        """Test mise à jour d'un profil"""
        # Given
        new_name = "Updated Admin Name"
        new_age = 30
        
        # When
        updated_profile = await profile_service.update(
            id=admin_profile.id,
            name=new_name,
            age=new_age
        )
        
        # Then
        assert updated_profile.name == new_name
        assert updated_profile.age == new_age
        assert updated_profile.email == admin_profile.email  # Inchangé
    
    @pytest.mark.asyncio
    async def test_update_email_success(self, profile_service, admin_profile):
        """Test mise à jour de l'email"""
        # Given
        new_email = "new_admin@example.com"
        
        # When
        updated_profile = await profile_service.update_email(
            id=admin_profile.id,
            new_email=new_email
        )
        
        # Then
        assert updated_profile.email == new_email
    
    @pytest.mark.asyncio
    async def test_update_email_duplicate(self, profile_service, admin_profile):
        """Test mise à jour avec email déjà utilisé"""
        # Given - Créer un autre utilisateur
        existing_email = "existing@example.com"
        await profile_service.create(
            email=existing_email,
            raw_password="password123",
            confirm_password="password123",
            name="Existing User"
        )
        
        # When/Then
        with pytest.raises(DuplicateProfileError):
            await profile_service.update_email(
                id=admin_profile.id,
                new_email=existing_email
            )
    
    @pytest.mark.asyncio
    async def test_update_password_success(self, profile_service):
        """Test mise à jour du mot de passe"""
        # Given - Créer un utilisateur
        email = "password_test@example.com"
        old_password = "old_password123"
        new_password = "new_password456"
        
        profile = await profile_service.create(
            email=email,
            raw_password=old_password,
            confirm_password=old_password,
            name="Password Test User"
        )
        
        # When
        await profile_service.update_password(
            id=profile.id,
            old_password=old_password,
            new_password=new_password
        )
        
        # Then - Vérifier qu'on peut se connecter avec le nouveau mot de passe
        authenticated = await profile_service.login(email, new_password)
        assert authenticated.id == profile.id
        
        # Et qu'on ne peut plus avec l'ancien
        with pytest.raises(AuthenticationError):
            await profile_service.login(email, old_password)
    
    @pytest.mark.asyncio
    async def test_update_password_wrong_old_password(self, profile_service, admin_profile):
        """Test mise à jour du mot de passe avec ancien mot de passe incorrect"""
        # When/Then
        with pytest.raises(AuthenticationError):
            await profile_service.update_password(
                id=admin_profile.id,
                old_password="wrong_old_password",
                new_password="new_password123"
            )
    
    @pytest.mark.asyncio
    async def test_update_roles_success(self, profile_service, admin_profile):
        """Test mise à jour des rôles"""
        # Given
        new_roles = ["admin", "coach", "user"]
        
        # When
        updated_profile = await profile_service.update_roles(
            id=admin_profile.id,
            roles=new_roles
        )
        
        # Then
        assert set(updated_profile.roles) == set(new_roles)
    
    @pytest.mark.asyncio
    async def test_update_roles_empty_list(self, profile_service, admin_profile):
        """Test mise à jour avec liste de rôles vide"""
        # When/Then
        with pytest.raises(ValueError):
            await profile_service.update_roles(
                id=admin_profile.id,
                roles=[]
            )
    
    @pytest.mark.asyncio
    async def test_delete_profile_success(self, profile_service):
        """Test suppression d'un profil"""
        # Given - Créer un utilisateur
        email = "to_delete@example.com"
        profile = await profile_service.create(
            email=email,
            raw_password="password123",
            confirm_password="password123",
            name="To Delete User"
        )
        
        # When
        await profile_service.delete(profile.id)
        
        # Then - Le profil n'existe plus
        with pytest.raises(NotFoundError):
            await profile_service.get_by_id(profile.id)
    
    @pytest.mark.asyncio
    async def test_delete_profile_not_found(self, profile_service):
        """Test suppression d'un profil inexistant"""
        # Given
        non_existent_id = uuid4()
        
        # When/Then
        with pytest.raises(NotFoundError):
            await profile_service.delete(non_existent_id)