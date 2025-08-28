import pytest
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import AsyncMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.domain.services.exercise import ExerciseService
from src.domain.ports.exercise_repository import ExerciseRepository
from src.domain.model.exercise import Exercise as DomainExercise
from src.domain.exceptions import NotFoundError


# Fixture pour simuler le repository (ExerciseRepository)
@pytest.fixture
def mock_repo():
    repo = AsyncMock(spec=ExerciseRepository)
    return repo


# Fixture pour créer une instance de ExerciseService avec le mock
@pytest.fixture
def exercise_service(mock_repo):
    return ExerciseService(repo=mock_repo)


# Helper function pour créer un exercice de test
def create_test_exercise(exercise_id=None, owner_id=None, name="Test Exercise"):
    return DomainExercise(
        id=exercise_id or uuid4(),
        owner_id=owner_id or uuid4(),
        name=name,
        description="Test description",
        created_at=datetime.utcnow()
    )


# Test de création d'exercice avec succès
@pytest.mark.asyncio
async def test_create_exercise_success(exercise_service, mock_repo):
    owner_id = uuid4()
    name = "Push-ups"
    description = "Standard push-ups exercise"
    
    created_exercise = create_test_exercise(owner_id=owner_id, name=name)
    mock_repo.add.return_value = created_exercise
    
    result = await exercise_service.create_exercise(
        owner_id=owner_id,
        name=name,
        description=description
    )
    
    mock_repo.add.assert_called_once()
    assert result == created_exercise


# Test de création d'exercice avec nom vide
@pytest.mark.asyncio
async def test_create_exercise_empty_name(exercise_service):
    owner_id = uuid4()
    
    with pytest.raises(ValueError, match="Exercise name cannot be empty"):
        await exercise_service.create_exercise(
            owner_id=owner_id,
            name=""
        )


# Test de création d'exercice sans description
@pytest.mark.asyncio
async def test_create_exercise_without_description(exercise_service, mock_repo):
    owner_id = uuid4()
    name = "Pull-ups"
    
    created_exercise = create_test_exercise(owner_id=owner_id, name=name)
    mock_repo.add.return_value = created_exercise
    
    result = await exercise_service.create_exercise(
        owner_id=owner_id,
        name=name
    )
    
    mock_repo.add.assert_called_once()
    assert result == created_exercise


# Test de suppression d'exercice
@pytest.mark.asyncio
async def test_delete_exercise(exercise_service, mock_repo):
    exercise_id = uuid4()
    
    await exercise_service.delete_exercise(exercise_id)
    
    mock_repo.delete.assert_called_once_with(exercise_id)


# Test de mise à jour d'exercice avec succès
@pytest.mark.asyncio
async def test_update_exercise_success(exercise_service, mock_repo):
    exercise_id = uuid4()
    exercise = create_test_exercise(exercise_id=exercise_id)
    updated_exercise = create_test_exercise(exercise_id=exercise_id)
    updated_exercise.name = "Updated Exercise"
    updated_exercise.description = "Updated description"
    
    mock_repo.find_by_id.return_value = exercise
    mock_repo.update.return_value = updated_exercise
    
    result = await exercise_service.update_exercise(
        exercise_id=exercise_id,
        name="Updated Exercise",
        description="Updated description"
    )
    
    mock_repo.find_by_id.assert_called_once_with(exercise_id)
    assert exercise.name == "Updated Exercise"
    assert exercise.description == "Updated description"
    mock_repo.update.assert_called_once_with(exercise)
    assert result == updated_exercise


# Test de mise à jour d'exercice - exercice non trouvé
@pytest.mark.asyncio
async def test_update_exercise_not_found(exercise_service, mock_repo):
    exercise_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Exercise {exercise_id} not found"):
        await exercise_service.update_exercise(
            exercise_id=exercise_id,
            name="New Name"
        )


# Test de mise à jour partielle d'exercice
@pytest.mark.asyncio
async def test_update_exercise_partial(exercise_service, mock_repo):
    exercise_id = uuid4()
    exercise = create_test_exercise(exercise_id=exercise_id)
    original_description = exercise.description
    
    mock_repo.find_by_id.return_value = exercise
    mock_repo.update.return_value = exercise
    
    await exercise_service.update_exercise(
        exercise_id=exercise_id,
        name="New Name Only"
    )
    
    assert exercise.name == "New Name Only"
    assert exercise.description == original_description  # Description inchangée


# Test de récupération des exercices du propriétaire avec succès
@pytest.mark.asyncio
async def test_get_exercises_mine_success(exercise_service, mock_repo):
    owner_id = uuid4()
    exercises = [
        create_test_exercise(owner_id=owner_id),
        create_test_exercise(owner_id=owner_id)
    ]
    
    mock_repo.find_all_owner.return_value = exercises
    
    result = await exercise_service.get_exercises_mine(owner_id)
    
    mock_repo.find_all_owner.assert_called_once_with(owner_id)
    assert result == exercises


# Test de récupération des exercices du propriétaire - aucun exercice
@pytest.mark.asyncio
async def test_get_exercises_mine_not_found(exercise_service, mock_repo):
    owner_id = uuid4()
    
    mock_repo.find_all_owner.return_value = []
    
    with pytest.raises(NotFoundError, match=f"No exercises found for owner {owner_id}"):
        await exercise_service.get_exercises_mine(owner_id)


# Test de récupération de tous les exercices avec succès
@pytest.mark.asyncio
async def test_get_all_exercises_success(exercise_service, mock_repo):
    exercises = [create_test_exercise(), create_test_exercise()]
    
    mock_repo.find_all.return_value = exercises
    
    result = await exercise_service.get_all_exercises()
    
    mock_repo.find_all.assert_called_once()
    assert result == exercises


# Test de récupération de tous les exercices - aucun exercice
@pytest.mark.asyncio
async def test_get_all_exercises_not_found(exercise_service, mock_repo):
    mock_repo.find_all.return_value = []
    
    with pytest.raises(NotFoundError, match="No exercises found"):
        await exercise_service.get_all_exercises()


# Test de récupération d'exercice par ID avec succès
@pytest.mark.asyncio
async def test_get_by_id_success(exercise_service, mock_repo):
    exercise_id = uuid4()
    exercise = create_test_exercise(exercise_id=exercise_id)
    
    mock_repo.find_by_id.return_value = exercise
    
    result = await exercise_service.get_by_id(exercise_id)
    
    mock_repo.find_by_id.assert_called_once_with(exercise_id)
    assert result == exercise


# Test de récupération d'exercice par ID - non trouvé
@pytest.mark.asyncio
async def test_get_by_id_not_found(exercise_service, mock_repo):
    exercise_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Exercise with id {exercise_id} not found"):
        await exercise_service.get_by_id(exercise_id)