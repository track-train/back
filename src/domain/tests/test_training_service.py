import pytest
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import AsyncMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.domain.services.training import TrainingService
from src.domain.ports.training_repository import TrainingRepository
from src.domain.model.training import Training as DomainTraining, Task as DomainTask, Validate as DomainValidate
from src.domain.exceptions import NotFoundError


# Fixture pour simuler le repository (TrainingRepository)
@pytest.fixture
def mock_repo():
    repo = AsyncMock(spec=TrainingRepository)
    return repo


# Fixture pour créer une instance de TrainingService avec le mock
@pytest.fixture
def training_service(mock_repo):
    return TrainingService(repo=mock_repo)


# Helper functions pour créer des objets de test
def create_test_training(training_id=None, owner_id=None, name="Test Training"):
    return DomainTraining(
        id=training_id or uuid4(),
        owner_id=owner_id or uuid4(),
        name=name,
        description="Test description",
        created_at=datetime.utcnow()
    )


def create_test_task(task_id=None, training_id=None, exercise_name="Test Exercise"):
    return DomainTask(
        id=task_id or uuid4(),
        training_id=training_id or uuid4(),
        exercise_name=exercise_name,
        rest_time=60,
        repetitions=10,
        set_number=3,
        method="standard",
        rir=2,
        updated_at=datetime.utcnow(),
        validate=[]
    )


def create_test_validate(validate_id=None, task_id=None, exercise_name="Test Exercise"):
    return DomainValidate(
        id=validate_id or uuid4(),
        task_id=task_id or uuid4(),
        exercise_name=exercise_name,
        rest_time=60,
        repetitions=10,
        set_number=3,
        rir=2,
        updated_at=datetime.utcnow(),
        succeeded_at=datetime.utcnow()
    )


# Tests pour Training
@pytest.mark.asyncio
async def test_get_training_success(training_service, mock_repo):
    training_id = uuid4()
    training = create_test_training(training_id=training_id)
    
    mock_repo.find_by_id.return_value = training
    
    result = await training_service.get_training(training_id)
    
    mock_repo.find_by_id.assert_called_once_with(training_id)
    assert result == training


@pytest.mark.asyncio
async def test_get_training_not_found(training_service, mock_repo):
    training_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Training {training_id} not found"):
        await training_service.get_training(training_id)


@pytest.mark.asyncio
async def test_create_training_success(training_service, mock_repo):
    owner_id = uuid4()
    name = "New Training"
    description = "Training description"
    
    created_training = create_test_training(owner_id=owner_id, name=name)
    mock_repo.add_training.return_value = created_training
    
    result = await training_service.create_training(owner_id, name, description)
    
    mock_repo.add_training.assert_called_once()
    assert result == created_training


@pytest.mark.asyncio
async def test_delete_training_success(training_service, mock_repo):
    training_id = uuid4()
    training = create_test_training(training_id=training_id)
    
    mock_repo.find_by_id.return_value = training
    
    await training_service.delete_training(training_id)
    
    mock_repo.find_by_id.assert_called_once_with(training_id)
    mock_repo.delete_training.assert_called_once_with(training_id)


@pytest.mark.asyncio
async def test_delete_training_not_found(training_service, mock_repo):
    training_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Training {training_id} not found"):
        await training_service.delete_training(training_id)


@pytest.mark.asyncio
async def test_update_training_success(training_service, mock_repo):
    training_id = uuid4()
    training = create_test_training(training_id=training_id)
    updated_training = create_test_training(training_id=training_id)
    updated_training.name = "Updated Training"
    updated_training.description = "Updated description"
    
    mock_repo.find_by_id.return_value = training
    mock_repo.update_training.return_value = updated_training
    
    result = await training_service.update_training(
        training_id=training_id,
        name="Updated Training",
        description="Updated description"
    )
    
    mock_repo.find_by_id.assert_called_once_with(training_id)
    assert training.name == "Updated Training"
    assert training.description == "Updated description"
    mock_repo.update_training.assert_called_once_with(training)
    assert result == updated_training


@pytest.mark.asyncio
async def test_update_training_not_found(training_service, mock_repo):
    training_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Training {training_id} not found"):
        await training_service.update_training(training_id, name="New Name")


@pytest.mark.asyncio
async def test_get_all_owner_trainings_success(training_service, mock_repo):
    owner_id = uuid4()
    trainings = [
        create_test_training(owner_id=owner_id),
        create_test_training(owner_id=owner_id)
    ]
    
    mock_repo.find_all_owner_trainings.return_value = trainings
    
    result = await training_service.get_all_owner_trainings(owner_id)
    
    mock_repo.find_all_owner_trainings.assert_called_once_with(owner_id)
    assert result == trainings


@pytest.mark.asyncio
async def test_get_all_owner_trainings_empty(training_service, mock_repo):
    owner_id = uuid4()
    
    mock_repo.find_all_owner_trainings.return_value = []
    
    result = await training_service.get_all_owner_trainings(owner_id)
    
    assert result == []


# Tests pour Task
@pytest.mark.asyncio
async def test_create_task_success(training_service, mock_repo):
    training_id = uuid4()
    training = create_test_training(training_id=training_id)
    exercise_name = "Push-ups"
    
    created_task = create_test_task(training_id=training_id, exercise_name=exercise_name)
    mock_repo.find_by_id.return_value = training
    mock_repo.add_task.return_value = created_task
    
    result = await training_service.create_task(
        training_id=training_id,
        exercise_name=exercise_name,
        rest_time=60,
        repetitions=10,
        set_number=3,
        method="standard",
        rir=2
    )
    
    mock_repo.find_by_id.assert_called_once_with(training_id)
    mock_repo.add_task.assert_called_once()
    assert result == created_task


@pytest.mark.asyncio
async def test_create_task_training_not_found(training_service, mock_repo):
    training_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Training {training_id} not found"):
        await training_service.create_task(
            training_id=training_id,
            exercise_name="Push-ups"
        )


@pytest.mark.asyncio
async def test_create_task_empty_exercise_name(training_service, mock_repo):
    training_id = uuid4()
    training = create_test_training(training_id=training_id)
    
    mock_repo.find_by_id.return_value = training
    
    with pytest.raises(ValueError, match="Exercise name is required"):
        await training_service.create_task(
            training_id=training_id,
            exercise_name=""
        )


@pytest.mark.asyncio
async def test_get_task_success(training_service, mock_repo):
    task_id = uuid4()
    task = create_test_task(task_id=task_id)
    
    mock_repo.find_task_by_id.return_value = task
    
    result = await training_service.get_task(task_id)
    
    mock_repo.find_task_by_id.assert_called_once_with(task_id)
    assert result == task


@pytest.mark.asyncio
async def test_get_task_not_found(training_service, mock_repo):
    task_id = uuid4()
    
    mock_repo.find_task_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Task {task_id} not found"):
        await training_service.get_task(task_id)


@pytest.mark.asyncio
async def test_update_task_success(training_service, mock_repo):
    task_id = uuid4()
    task = create_test_task(task_id=task_id)
    updated_task = create_test_task(task_id=task_id)
    
    mock_repo.find_task_by_id.return_value = task
    mock_repo.update_task.return_value = updated_task
    
    result = await training_service.update_task(
        task_id=task_id,
        exercise_name="Updated Exercise",
        rest_time=90,
        repetitions=15
    )
    
    mock_repo.find_task_by_id.assert_called_once_with(task_id)
    assert task.exercise_name == "Updated Exercise"
    assert task.rest_time == 90
    assert task.repetitions == 15
    mock_repo.update_task.assert_called_once_with(task)
    assert result == updated_task


@pytest.mark.asyncio
async def test_update_task_not_found(training_service, mock_repo):
    task_id = uuid4()
    
    mock_repo.find_task_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Task {task_id} not found"):
        await training_service.update_task(task_id, exercise_name="New Exercise")


@pytest.mark.asyncio
async def test_delete_task_success(training_service, mock_repo):
    task_id = uuid4()
    task = create_test_task(task_id=task_id)
    
    mock_repo.find_task_by_id.return_value = task
    
    await training_service.delete_task(task_id)
    
    mock_repo.find_task_by_id.assert_called_once_with(task_id)
    mock_repo.delete_task.assert_called_once_with(task_id)


@pytest.mark.asyncio
async def test_delete_task_not_found(training_service, mock_repo):
    task_id = uuid4()
    
    mock_repo.find_task_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Task {task_id} not found"):
        await training_service.delete_task(task_id)


@pytest.mark.asyncio
async def test_list_tasks_for_training_success(training_service, mock_repo):
    training_id = uuid4()
    tasks = [
        create_test_task(training_id=training_id),
        create_test_task(training_id=training_id)
    ]
    
    mock_repo.find_tasks_by_training_id.return_value = tasks
    
    result = await training_service.list_tasks_for_training(training_id)
    
    mock_repo.find_tasks_by_training_id.assert_called_once_with(training_id)
    assert result == tasks


@pytest.mark.asyncio
async def test_list_tasks_for_training_empty(training_service, mock_repo):
    training_id = uuid4()
    
    mock_repo.find_tasks_by_training_id.return_value = None
    
    result = await training_service.list_tasks_for_training(training_id)
    
    assert result == []


# Tests pour Validate
@pytest.mark.asyncio
async def test_create_validate_success(training_service, mock_repo):
    task_id = uuid4()
    task = create_test_task(task_id=task_id)
    
    created_validate = create_test_validate(task_id=task_id, exercise_name=task.exercise_name)
    mock_repo.find_task_by_id.return_value = task
    mock_repo.add_validate.return_value = created_validate
    
    result = await training_service.create_validate(
        task_id=task_id,
        rest_time=60,
        repetitions=10,
        set_number=3,
        rir=2
    )
    
    mock_repo.find_task_by_id.assert_called_once_with(task_id)
    mock_repo.add_validate.assert_called_once()
    assert result == created_validate


@pytest.mark.asyncio
async def test_create_validate_task_not_found(training_service, mock_repo):
    task_id = uuid4()
    
    mock_repo.find_task_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Task {task_id} not found"):
        await training_service.create_validate(task_id=task_id)


@pytest.mark.asyncio
async def test_get_validates_for_task_success(training_service, mock_repo):
    task_id = uuid4()
    validates = [
        create_test_validate(task_id=task_id),
        create_test_validate(task_id=task_id)
    ]
    
    mock_repo.find_validate_by_task_id.return_value = validates
    
    result = await training_service.get_validates_for_task(task_id)
    
    mock_repo.find_validate_by_task_id.assert_called_once_with(task_id)
    assert result == validates


@pytest.mark.asyncio
async def test_get_validates_for_task_empty(training_service, mock_repo):
    task_id = uuid4()
    
    mock_repo.find_validate_by_task_id.return_value = []
    
    result = await training_service.get_validates_for_task(task_id)
    
    assert result == []


@pytest.mark.asyncio
async def test_delete_validate_success(training_service, mock_repo):
    validate_id = uuid4()
    validate = create_test_validate(validate_id=validate_id)
    
    mock_repo.find_validate_by_id.return_value = validate
    
    await training_service.delete_validate(validate_id)
    
    mock_repo.find_validate_by_id.assert_called_once_with(validate_id)
    mock_repo.delete_validate.assert_called_once_with(validate_id)


@pytest.mark.asyncio
async def test_delete_validate_not_found(training_service, mock_repo):
    validate_id = uuid4()
    
    mock_repo.find_validate_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Validation {validate_id} not found"):
        await training_service.delete_validate(validate_id)


@pytest.mark.asyncio
async def test_get_validate_by_training_id_success(training_service, mock_repo):
    training_id = uuid4()
    training = create_test_training(training_id=training_id)
    validates = [create_test_validate(), create_test_validate()]
    
    mock_repo.find_by_id.return_value = training
    mock_repo.find_all_validates_by_training_id.return_value = validates
    
    result = await training_service.get_validate_by_training_id(training_id)
    
    mock_repo.find_by_id.assert_called_once_with(training_id)
    mock_repo.find_all_validates_by_training_id.assert_called_once_with(training_id)
    assert result == validates


@pytest.mark.asyncio
async def test_get_validate_by_training_id_training_not_found(training_service, mock_repo):
    training_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Training {training_id} not found"):
        await training_service.get_validate_by_training_id(training_id)