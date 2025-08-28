import pytest
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import AsyncMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.domain.services.group import GroupService
from src.domain.ports.group_repository import GroupRepository
from src.domain.model.group import Group as DomainGroup
from src.domain.model.profile import Profile as DomainProfile
from src.domain.exceptions import NotFoundError


# Fixture pour simuler le repository (GroupRepository)
@pytest.fixture
def mock_repo():
    repo = AsyncMock(spec=GroupRepository)
    return repo


# Fixture pour créer une instance de GroupService avec le mock
@pytest.fixture
def group_service(mock_repo):
    return GroupService(repo=mock_repo)


# Helper function pour créer un groupe de test
def create_test_group(group_id=None, owner_id=None, name="Test Group"):
    return DomainGroup(
        id=group_id or uuid4(),
        owner_id=owner_id or uuid4(),
        name=name,
        description="Test description",
        created_at=datetime.utcnow()
    )


# Helper function pour créer un profil de test
def create_test_profile(profile_id=None, roles=None):
    profile = DomainProfile(
        id=profile_id or uuid4(),
        email="test@example.com",
        password="hashedpassword",
        name="Test User",
        roles=roles or ["user"]
    )
    return profile


# Test de création de groupe avec succès
@pytest.mark.asyncio
async def test_create_group_success(group_service, mock_repo):
    owner_id = uuid4()
    name = "New Group"
    description = "Group description"
    
    # Simuler le retour du repository
    created_group = create_test_group(owner_id=owner_id, name=name)
    mock_repo.add.return_value = created_group
    
    result = await group_service.create(
        owner_id=owner_id,
        name=name,
        description=description
    )
    
    mock_repo.add.assert_called_once()
    assert result == created_group


# Test de création de groupe avec nom vide
@pytest.mark.asyncio
async def test_create_group_empty_name(group_service):
    owner_id = uuid4()
    
    with pytest.raises(ValueError, match="Group name cannot be empty"):
        await group_service.create(
            owner_id=owner_id,
            name=""
        )


# Test de suppression de groupe avec succès
@pytest.mark.asyncio
async def test_delete_group_success(group_service, mock_repo):
    group_id = uuid4()
    group = create_test_group(group_id=group_id)
    
    mock_repo.find_by_id.return_value = group
    
    await group_service.delete(group_id)
    
    mock_repo.find_by_id.assert_called_once_with(group_id)
    mock_repo.delete.assert_called_once_with(group_id)


# Test de suppression de groupe non existant
@pytest.mark.asyncio
async def test_delete_group_not_found(group_service, mock_repo):
    group_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Group with id {group_id} not found"):
        await group_service.delete(group_id)


# Test de mise à jour de groupe avec succès
@pytest.mark.asyncio
async def test_update_group_success(group_service, mock_repo):
    group = create_test_group()
    updated_group = create_test_group(group_id=group.id)
    updated_group.name = "Updated Name"
    
    mock_repo.find_by_id.return_value = group
    mock_repo.update.return_value = updated_group
    
    result = await group_service.update(updated_group)
    
    mock_repo.find_by_id.assert_called_once_with(group.id)
    mock_repo.update.assert_called_once_with(updated_group)
    assert result == updated_group


# Test de mise à jour de groupe non existant
@pytest.mark.asyncio
async def test_update_group_not_found(group_service, mock_repo):
    group = create_test_group()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Group with id {group.id} not found"):
        await group_service.update(group)


# Test d'ajout de membre avec succès
@pytest.mark.asyncio
async def test_add_member_success(group_service, mock_repo):
    group_id = uuid4()
    user_id = uuid4()
    group = create_test_group(group_id=group_id)
    user = create_test_profile(profile_id=user_id)
    
    mock_repo.find_by_id.return_value = group
    
    # Mock du container et profile_service
    with patch('src.container.container') as mock_container:
        mock_profile_service = AsyncMock()
        mock_profile_service.get_by_id.return_value = user
        mock_container.get_profile_service.return_value = mock_profile_service
        
        await group_service.add_member(group_id, user_id)
        
        mock_repo.find_by_id.assert_called_once_with(group_id)
        mock_profile_service.get_by_id.assert_called_once_with(user_id)
        mock_repo.add_member.assert_called_once_with(group_id, user_id)


# Test d'ajout de membre - groupe non trouvé
@pytest.mark.asyncio
async def test_add_member_group_not_found(group_service, mock_repo):
    group_id = uuid4()
    user_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Group {group_id} not found"):
        await group_service.add_member(group_id, user_id)


# Test d'ajout de membre - utilisateur non trouvé
@pytest.mark.asyncio
async def test_add_member_user_not_found(group_service, mock_repo):
    group_id = uuid4()
    user_id = uuid4()
    group = create_test_group(group_id=group_id)
    
    mock_repo.find_by_id.return_value = group
    
    with patch('src.container.container') as mock_container:
        mock_profile_service = AsyncMock()
        mock_profile_service.get_by_id.side_effect = NotFoundError(f"User {user_id} not found")
        mock_container.get_profile_service.return_value = mock_profile_service
        
        with pytest.raises(NotFoundError, match=f"User {user_id} not found"):
            await group_service.add_member(group_id, user_id)


# Test de suppression de membre avec succès
@pytest.mark.asyncio
async def test_remove_member_success(group_service, mock_repo):
    group_id = uuid4()
    user_id = uuid4()
    group = create_test_group(group_id=group_id)
    member = create_test_profile(profile_id=user_id)
    
    mock_repo.find_by_id.return_value = group
    mock_repo.list_members.return_value = [member]
    
    await group_service.remove_member(group_id, user_id)
    
    mock_repo.find_by_id.assert_called_once_with(group_id)
    mock_repo.list_members.assert_called_once_with(group_id)
    mock_repo.remove_member.assert_called_once_with(group_id, user_id)


# Test de suppression de membre - groupe non trouvé
@pytest.mark.asyncio
async def test_remove_member_group_not_found(group_service, mock_repo):
    group_id = uuid4()
    user_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Group with id {group_id} not found"):
        await group_service.remove_member(group_id, user_id)


# Test de suppression de membre - membre non trouvé
@pytest.mark.asyncio
async def test_remove_member_not_found(group_service, mock_repo):
    group_id = uuid4()
    user_id = uuid4()
    other_user_id = uuid4()
    group = create_test_group(group_id=group_id)
    other_member = create_test_profile(profile_id=other_user_id)
    
    mock_repo.find_by_id.return_value = group
    mock_repo.list_members.return_value = [other_member]
    
    with pytest.raises(NotFoundError, match=f"User with id {user_id} is not a member of group {group_id}"):
        await group_service.remove_member(group_id, user_id)


# Test de liste des groupes du propriétaire avec succès
@pytest.mark.asyncio
async def test_list_owner_groups_success(group_service, mock_repo):
    owner_id = uuid4()
    groups = [create_test_group(owner_id=owner_id), create_test_group(owner_id=owner_id)]
    
    mock_repo.find_by_owner_id.return_value = groups
    
    result = await group_service.list_owner_groups(owner_id)
    
    mock_repo.find_by_owner_id.assert_called_once_with(owner_id)
    assert result == groups


# Test de liste des groupes du propriétaire - aucun groupe trouvé
@pytest.mark.asyncio
async def test_list_owner_groups_not_found(group_service, mock_repo):
    owner_id = uuid4()
    
    mock_repo.find_by_owner_id.return_value = []
    
    with pytest.raises(NotFoundError, match=f"No groups found for owner with id {owner_id}"):
        await group_service.list_owner_groups(owner_id)


# Test de liste des membres avec succès
@pytest.mark.asyncio
async def test_list_members_success(group_service, mock_repo):
    group_id = uuid4()
    group = create_test_group(group_id=group_id)
    members = [create_test_profile(), create_test_profile()]
    
    mock_repo.find_by_id.return_value = group
    mock_repo.list_members.return_value = members
    
    result = await group_service.list_members(group_id)
    
    mock_repo.find_by_id.assert_called_once_with(group_id)
    mock_repo.list_members.assert_called_once_with(group_id)
    assert result == members


# Test de liste des membres - groupe non trouvé
@pytest.mark.asyncio
async def test_list_members_group_not_found(group_service, mock_repo):
    group_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Group with id {group_id} not found"):
        await group_service.list_members(group_id)


# Test de liste des membres - aucun membre
@pytest.mark.asyncio
async def test_list_members_empty(group_service, mock_repo):
    group_id = uuid4()
    group = create_test_group(group_id=group_id)
    
    mock_repo.find_by_id.return_value = group
    mock_repo.list_members.return_value = None
    
    result = await group_service.list_members(group_id)
    
    assert result == []


# Test de récupération de tous les groupes avec succès
@pytest.mark.asyncio
async def test_get_all_groups_success(group_service, mock_repo):
    groups = [create_test_group(), create_test_group()]
    
    mock_repo.find_all_groups.return_value = groups
    
    result = await group_service.get_all_groups()
    
    mock_repo.find_all_groups.assert_called_once()
    assert result == groups


# Test de récupération de tous les groupes - aucun groupe trouvé
@pytest.mark.asyncio
async def test_get_all_groups_not_found(group_service, mock_repo):
    mock_repo.find_all_groups.return_value = []
    
    with pytest.raises(NotFoundError, match="No groups found"):
        await group_service.get_all_groups()


# Test de récupération de groupe par ID avec succès
@pytest.mark.asyncio
async def test_get_by_id_success(group_service, mock_repo):
    group_id = uuid4()
    group = create_test_group(group_id=group_id)
    
    mock_repo.find_by_id.return_value = group
    
    result = await group_service.get_by_id(group_id)
    
    mock_repo.find_by_id.assert_called_once_with(group_id)
    assert result == group


# Test de récupération de groupe par ID - non trouvé
@pytest.mark.asyncio
async def test_get_by_id_not_found(group_service, mock_repo):
    group_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Group with id {group_id} not found"):
        await group_service.get_by_id(group_id)


# Test de récupération des coachs avec succès
@pytest.mark.asyncio
async def test_get_my_coaches_success(group_service, mock_repo):
    user_id = uuid4()
    coach_id_1 = uuid4()
    coach_id_2 = uuid4()
    
    groups = [
        create_test_group(owner_id=coach_id_1),
        create_test_group(owner_id=coach_id_2)
    ]
    
    coach_1 = create_test_profile(profile_id=coach_id_1, roles=["coach"])
    coach_2 = create_test_profile(profile_id=coach_id_2, roles=["coach"])
    
    mock_repo.find_groups_by_member_id.return_value = groups
    
    with patch('src.container.container') as mock_container:
        mock_profile_service = AsyncMock()
        mock_profile_service.get_by_id.side_effect = [coach_1, coach_2]
        mock_container.get_profile_service.return_value = mock_profile_service
        
        result = await group_service.get_my_coaches(user_id)
        
        mock_repo.find_groups_by_member_id.assert_called_once_with(user_id)
        assert len(result) == 2
        assert coach_1 in result
        assert coach_2 in result


# Test de récupération des coachs - aucun groupe trouvé
@pytest.mark.asyncio
async def test_get_my_coaches_no_groups(group_service, mock_repo):
    user_id = uuid4()
    
    mock_repo.find_groups_by_member_id.return_value = []
    
    with pytest.raises(NotFoundError, match=f"No groups found for user {user_id}"):
        await group_service.get_my_coaches(user_id)


# Test de récupération des coachs - aucun coach trouvé
@pytest.mark.asyncio
async def test_get_my_coaches_no_coaches(group_service, mock_repo):
    user_id = uuid4()
    owner_id = uuid4()
    
    groups = [create_test_group(owner_id=owner_id)]
    non_coach = create_test_profile(profile_id=owner_id, roles=["user"])
    
    mock_repo.find_groups_by_member_id.return_value = groups
    
    with patch('src.container.container') as mock_container:
        mock_profile_service = AsyncMock()
        mock_profile_service.get_by_id.return_value = non_coach
        mock_container.get_profile_service.return_value = mock_profile_service
        
        with pytest.raises(NotFoundError, match="No coaches found in your groups"):
            await group_service.get_my_coaches(user_id)


# Test de récupération des coachs - coach non trouvé (continue)
@pytest.mark.asyncio
async def test_get_my_coaches_coach_not_found_continues(group_service, mock_repo):
    user_id = uuid4()
    coach_id_1 = uuid4()
    coach_id_2 = uuid4()
    
    groups = [
        create_test_group(owner_id=coach_id_1),
        create_test_group(owner_id=coach_id_2)
    ]
    
    coach_2 = create_test_profile(profile_id=coach_id_2, roles=["coach"])
    
    mock_repo.find_groups_by_member_id.return_value = groups
    
    with patch('src.container.container') as mock_container:
        mock_profile_service = AsyncMock()
        # Premier coach non trouvé, deuxième trouvé
        mock_profile_service.get_by_id.side_effect = [
            NotFoundError("Coach not found"),
            coach_2
        ]
        mock_container.get_profile_service.return_value = mock_profile_service
        
        result = await group_service.get_my_coaches(user_id)
        
        assert len(result) == 1
        assert coach_2 in result