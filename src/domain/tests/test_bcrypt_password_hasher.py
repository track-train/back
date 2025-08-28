import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


from src.domain.lib.security import BcryptPasswordHasher


@pytest.fixture
def password_hasher():
    return BcryptPasswordHasher()


def test_hash_password(password_hasher):
    """Test que le hachage d'un mot de passe fonctionne"""
    password = "test_password_123"
    
    hashed = password_hasher.hash(password)
    
    # Vérifier que le hash est généré et différent du mot de passe original
    assert hashed is not None
    assert hashed != password
    assert len(hashed) > 0
    # Bcrypt hashes commencent généralement par $2b$
    assert hashed.startswith("$2b$")


def test_hash_different_passwords_produce_different_hashes(password_hasher):
    """Test que des mots de passe différents produisent des hashes différents"""
    password1 = "password123"
    password2 = "password456"
    
    hash1 = password_hasher.hash(password1)
    hash2 = password_hasher.hash(password2)
    
    assert hash1 != hash2


def test_hash_same_password_produces_different_salts(password_hasher):
    """Test que le même mot de passe produit des hashes différents (à cause du salt)"""
    password = "same_password"
    
    hash1 = password_hasher.hash(password)
    hash2 = password_hasher.hash(password)
    
    # Les hashes doivent être différents à cause du salt aléatoire
    assert hash1 != hash2


def test_verify_correct_password(password_hasher):
    """Test que la vérification d'un mot de passe correct fonctionne"""
    password = "correct_password"
    
    hashed = password_hasher.hash(password)
    result = password_hasher.verify(password, hashed)
    
    assert result is True


def test_verify_incorrect_password(password_hasher):
    """Test que la vérification d'un mot de passe incorrect échoue"""
    correct_password = "correct_password"
    wrong_password = "wrong_password"
    
    hashed = password_hasher.hash(correct_password)
    result = password_hasher.verify(wrong_password, hashed)
    
    assert result is False


def test_verify_empty_password(password_hasher):
    """Test que la vérification avec un mot de passe vide échoue"""
    password = "non_empty_password"
    
    hashed = password_hasher.hash(password)
    result = password_hasher.verify("", hashed)
    
    assert result is False


def test_verify_with_invalid_hash(password_hasher):
    """Test que la vérification avec un hash invalide retourne False au lieu de lever une exception"""
    password = "test_password"
    invalid_hash = "invalid_hash_string"
    
    # Au lieu de lever une exception, on s'attend à ce que verify retourne False
    result = password_hasher.verify(password, invalid_hash)
    
    assert result is False


def test_hash_empty_string(password_hasher):
    """Test que le hachage d'une chaîne vide fonctionne"""
    empty_password = ""
    
    hashed = password_hasher.hash(empty_password)
    
    assert hashed is not None
    assert len(hashed) > 0
    assert hashed.startswith("$2b$")


def test_verify_empty_string_with_its_hash(password_hasher):
    """Test que la vérification d'une chaîne vide avec son propre hash fonctionne"""
    empty_password = ""
    
    hashed = password_hasher.hash(empty_password)
    result = password_hasher.verify(empty_password, hashed)
    
    assert result is True


def test_hash_special_characters(password_hasher):
    """Test que le hachage de caractères spéciaux fonctionne"""
    special_password = "pàssw0rd!@#$%^&*()_+-=[]{}|;':\",./<>?"
    
    hashed = password_hasher.hash(special_password)
    result = password_hasher.verify(special_password, hashed)
    
    assert hashed is not None
    assert result is True


def test_hash_unicode_characters(password_hasher):
    """Test que le hachage de caractères Unicode fonctionne"""
    unicode_password = "пароль123🔒"
    
    hashed = password_hasher.hash(unicode_password)
    result = password_hasher.verify(unicode_password, hashed)
    
    assert hashed is not None
    assert result is True


def test_hash_long_password(password_hasher):
    """Test que le hachage d'un mot de passe très long fonctionne"""
    long_password = "a" * 1000  # Mot de passe de 1000 caractères
    
    hashed = password_hasher.hash(long_password)
    result = password_hasher.verify(long_password, hashed)
    
    assert hashed is not None
    assert result is True