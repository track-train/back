import pytest
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import AsyncMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.domain.services.diet import DietService
from src.domain.ports.diet_repository import DietRepository
from src.domain.model.diet import Diet as DomainDiet, MacroPlan as DomainMacroPlan, MealPlan as DomainMealPlan, MealItem as DomainMealItem
from src.domain.exceptions import NotFoundError


# Fixture pour simuler le repository (DietRepository)
@pytest.fixture
def mock_repo():
    repo = AsyncMock(spec=DietRepository)
    return repo


# Fixture pour créer une instance de DietService avec le mock
@pytest.fixture
def diet_service(mock_repo):
    return DietService(repo=mock_repo)


# Helper functions pour créer des objets de test
def create_test_diet(diet_id=None, owner_id=None, name="Test Diet"):
    return DomainDiet(
        id=diet_id or uuid4(),
        owner_id=owner_id or uuid4(),
        name=name,
        description="Test description",
        created_at=datetime.utcnow()
    )


def create_test_macro_plan(plan_id=None, diet_id=None, name="Test Macro Plan"):
    return DomainMacroPlan(
        id=plan_id or uuid4(),
        diet_id=diet_id or uuid4(),
        name=name,
        carbohydrates=100.0,
        lipids=50.0,
        protein=75.0,
        fiber=25.0,
        water=2000.0,
        kilocalorie=1800.0
    )


def create_test_meal_item(timing="breakfast", food="eggs"):
    # Correction : utiliser les bons paramètres selon le modèle
    return DomainMealItem(
        timing=timing,
        food=food
    )


def create_test_meal_plan(plan_id=None, diet_id=None, name="Test Meal Plan"):
    meals = [
        create_test_meal_item("breakfast", "eggs and toast"),
        create_test_meal_item("lunch", "chicken salad")
    ]
    return DomainMealPlan(
        id=plan_id or uuid4(),
        diet_id=diet_id or uuid4(),
        name=name,
        meals=meals
    )


# Tests pour Diet
@pytest.mark.asyncio
async def test_create_diet_success(diet_service, mock_repo):
    owner_id = uuid4()
    name = "Mediterranean Diet"
    description = "Healthy Mediterranean diet plan"
    
    created_diet = create_test_diet(owner_id=owner_id, name=name)
    mock_repo.add_diet.return_value = created_diet
    
    result = await diet_service.create_diet(
        owner_id=owner_id,
        name=name,
        description=description
    )
    
    mock_repo.add_diet.assert_called_once()
    assert result == created_diet


@pytest.mark.asyncio
async def test_create_diet_empty_name(diet_service):
    owner_id = uuid4()
    
    with pytest.raises(ValueError, match="Diet name cannot be empty"):
        await diet_service.create_diet(
            owner_id=owner_id,
            name=""
        )


@pytest.mark.asyncio
async def test_create_diet_without_description(diet_service, mock_repo):
    owner_id = uuid4()
    name = "Keto Diet"
    
    created_diet = create_test_diet(owner_id=owner_id, name=name)
    mock_repo.add_diet.return_value = created_diet
    
    result = await diet_service.create_diet(
        owner_id=owner_id,
        name=name
    )
    
    mock_repo.add_diet.assert_called_once()
    assert result == created_diet


@pytest.mark.asyncio
async def test_get_diet_success(diet_service, mock_repo):
    diet_id = uuid4()
    diet = create_test_diet(diet_id=diet_id)
    
    mock_repo.find_by_id.return_value = diet
    
    result = await diet_service.get_diet(diet_id)
    
    mock_repo.find_by_id.assert_called_once_with(diet_id)
    assert result == diet


@pytest.mark.asyncio
async def test_get_diet_not_found(diet_service, mock_repo):
    diet_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Diet {diet_id} not found"):
        await diet_service.get_diet(diet_id)


@pytest.mark.asyncio
async def test_list_owner_diets(diet_service, mock_repo):
    owner_id = uuid4()
    diets = [
        create_test_diet(owner_id=owner_id),
        create_test_diet(owner_id=owner_id)
    ]
    
    mock_repo.find_all_owner_diets.return_value = diets
    
    result = await diet_service.list_owner_diets(owner_id)
    
    mock_repo.find_all_owner_diets.assert_called_once_with(owner_id)
    assert result == diets


@pytest.mark.asyncio
async def test_update_diet_success(diet_service, mock_repo):
    diet_id = uuid4()
    diet = create_test_diet(diet_id=diet_id)
    updated_diet = create_test_diet(diet_id=diet_id)
    updated_diet.name = "Updated Diet"
    updated_diet.description = "Updated description"
    
    mock_repo.find_by_id.return_value = diet
    mock_repo.update_diet.return_value = updated_diet
    
    result = await diet_service.update_diet(
        diet_id=diet_id,
        name="Updated Diet",
        description="Updated description"
    )
    
    mock_repo.find_by_id.assert_called_once_with(diet_id)
    assert diet.name == "Updated Diet"
    assert diet.description == "Updated description"
    mock_repo.update_diet.assert_called_once_with(diet)
    assert result == updated_diet


@pytest.mark.asyncio
async def test_update_diet_not_found(diet_service, mock_repo):
    diet_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Diet {diet_id} not found"):
        await diet_service.update_diet(diet_id, name="New Name")


@pytest.mark.asyncio
async def test_update_diet_partial(diet_service, mock_repo):
    diet_id = uuid4()
    diet = create_test_diet(diet_id=diet_id)
    original_description = diet.description
    
    mock_repo.find_by_id.return_value = diet
    mock_repo.update_diet.return_value = diet
    
    await diet_service.update_diet(
        diet_id=diet_id,
        name="New Name Only"
    )
    
    assert diet.name == "New Name Only"
    assert diet.description == original_description  # Description inchangée


@pytest.mark.asyncio
async def test_delete_diet_success(diet_service, mock_repo):
    diet_id = uuid4()
    diet = create_test_diet(diet_id=diet_id)
    
    mock_repo.find_by_id.return_value = diet
    
    await diet_service.delete_diet(diet_id)
    
    mock_repo.find_by_id.assert_called_once_with(diet_id)
    mock_repo.delete_diet.assert_called_once_with(diet_id)


@pytest.mark.asyncio
async def test_delete_diet_not_found(diet_service, mock_repo):
    diet_id = uuid4()
    
    mock_repo.find_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"Diet {diet_id} not found"):
        await diet_service.delete_diet(diet_id)


# Tests pour MacroPlan
@pytest.mark.asyncio
async def test_create_macro_plan_success(diet_service, mock_repo):
    diet_id = uuid4()
    name = "High Protein Plan"
    
    created_plan = create_test_macro_plan(diet_id=diet_id, name=name)
    mock_repo.add_macro_plan.return_value = created_plan
    
    result = await diet_service.create_macro_plan(
        diet_id=diet_id,
        name=name,
        carbohydrates=100.0,
        lipids=50.0,
        protein=75.0,
        fiber=25.0,
        water=2000.0,
        kilocalorie=1800.0
    )
    
    mock_repo.add_macro_plan.assert_called_once()
    assert result == created_plan


@pytest.mark.asyncio
async def test_create_macro_plan_empty_name(diet_service):
    diet_id = uuid4()
    
    with pytest.raises(ValueError, match="Name is required"):
        await diet_service.create_macro_plan(
            diet_id=diet_id,
            name="",
            carbohydrates=100.0,
            lipids=50.0,
            protein=75.0,
            fiber=25.0,
            water=2000.0,
            kilocalorie=1800.0
        )


@pytest.mark.asyncio
async def test_get_macro_plans_for_diet(diet_service, mock_repo):
    diet_id = uuid4()
    plans = [
        create_test_macro_plan(diet_id=diet_id),
        create_test_macro_plan(diet_id=diet_id)
    ]
    
    mock_repo.find_macro_plans_by_diet_id.return_value = plans
    
    result = await diet_service.get_macro_plans_for_diet(diet_id)
    
    mock_repo.find_macro_plans_by_diet_id.assert_called_once_with(diet_id)
    assert result == plans


@pytest.mark.asyncio
async def test_get_macro_plans_by_user_id(diet_service, mock_repo):
    user_id = uuid4()
    plans = [create_test_macro_plan(), create_test_macro_plan()]
    
    mock_repo.find_macro_plans_by_user_id.return_value = plans
    
    result = await diet_service.get_macro_plans_by_user_id(user_id)
    
    mock_repo.find_macro_plans_by_user_id.assert_called_once_with(user_id)
    assert result == plans


@pytest.mark.asyncio
async def test_get_macro_plan_success(diet_service, mock_repo):
    plan_id = uuid4()
    plan = create_test_macro_plan(plan_id=plan_id)
    
    mock_repo.find_macro_plan_by_id.return_value = plan
    
    result = await diet_service.get_macro_plan(plan_id)
    
    mock_repo.find_macro_plan_by_id.assert_called_once_with(plan_id)
    assert result == plan


@pytest.mark.asyncio
async def test_get_macro_plan_not_found(diet_service, mock_repo):
    plan_id = uuid4()
    
    mock_repo.find_macro_plan_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"MacroPlan {plan_id} not found"):
        await diet_service.get_macro_plan(plan_id)


@pytest.mark.asyncio
async def test_update_macro_plan_success(diet_service, mock_repo):
    plan_id = uuid4()
    plan = create_test_macro_plan(plan_id=plan_id)
    updated_plan = create_test_macro_plan(plan_id=plan_id)
    
    mock_repo.find_macro_plan_by_id.return_value = plan
    mock_repo.update_macro_plan.return_value = updated_plan
    
    result = await diet_service.update_macro_plan(
        plan_id=plan_id,
        name="Updated Plan",
        protein=100.0,
        kilocalorie=2000.0
    )
    
    mock_repo.find_macro_plan_by_id.assert_called_once_with(plan_id)
    assert plan.name == "Updated Plan"
    assert plan.protein == 100.0
    assert plan.kilocalorie == 2000.0
    mock_repo.update_macro_plan.assert_called_once_with(plan)
    assert result == updated_plan


@pytest.mark.asyncio
async def test_delete_macro_plan_success(diet_service, mock_repo):
    plan_id = uuid4()
    plan = create_test_macro_plan(plan_id=plan_id)
    
    mock_repo.find_macro_plan_by_id.return_value = plan
    
    await diet_service.delete_macro_plan(plan_id)
    
    mock_repo.find_macro_plan_by_id.assert_called_once_with(plan_id)
    mock_repo.delete_macro_plan.assert_called_once_with(plan_id)


@pytest.mark.asyncio
async def test_delete_macro_plan_not_found(diet_service, mock_repo):
    plan_id = uuid4()
    
    mock_repo.find_macro_plan_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"MacroPlan {plan_id} not found"):
        await diet_service.delete_macro_plan(plan_id)


# Tests pour MealPlan
@pytest.mark.asyncio
async def test_create_meal_plan_success(diet_service, mock_repo):
    diet_id = uuid4()
    name = "Daily Meal Plan"
    
    # Mock des objets meals pour simuler le .model_dump()
    class MockMeal:
        def model_dump(self):
            return {"timing": "breakfast", "food": "eggs and toast"}
    
    meals = [MockMeal(), MockMeal()]
    created_plan = create_test_meal_plan(diet_id=diet_id, name=name)
    mock_repo.add_meal_plan.return_value = created_plan
    
    result = await diet_service.create_meal_plan(
        diet_id=diet_id,
        name=name,
        meals=meals
    )
    
    mock_repo.add_meal_plan.assert_called_once()
    assert result == created_plan


@pytest.mark.asyncio
async def test_create_meal_plan_empty_name(diet_service):
    diet_id = uuid4()
    
    class MockMeal:
        def model_dump(self):
            return {"timing": "breakfast", "food": "eggs and toast"}
    
    meals = [MockMeal()]
    
    with pytest.raises(ValueError, match="Meal Plan name cannot be empty"):
        await diet_service.create_meal_plan(
            diet_id=diet_id,
            name="",
            meals=meals
        )


@pytest.mark.asyncio
async def test_get_meal_plan_by_id_success(diet_service, mock_repo):
    plan_id = uuid4()
    plan = create_test_meal_plan(plan_id=plan_id)
    
    mock_repo.find_meal_plan_by_id.return_value = plan
    
    result = await diet_service.get_meal_plan_by_id(plan_id)
    
    mock_repo.find_meal_plan_by_id.assert_called_once_with(plan_id)
    assert result == plan


@pytest.mark.asyncio
async def test_get_meal_plan_by_id_not_found(diet_service, mock_repo):
    plan_id = uuid4()
    
    mock_repo.find_meal_plan_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"MealPlan {plan_id} not found"):
        await diet_service.get_meal_plan_by_id(plan_id)


@pytest.mark.asyncio
async def test_get_meal_plans_by_diet(diet_service, mock_repo):
    diet_id = uuid4()
    plans = [
        create_test_meal_plan(diet_id=diet_id),
        create_test_meal_plan(diet_id=diet_id)
    ]
    
    mock_repo.find_meal_plans_by_diet_id.return_value = plans
    
    result = await diet_service.get_meal_plans_by_diet(diet_id)
    
    mock_repo.find_meal_plans_by_diet_id.assert_called_once_with(diet_id)
    assert result == plans


@pytest.mark.asyncio
async def test_get_meal_plans_by_user(diet_service, mock_repo):
    user_id = uuid4()
    plans = [create_test_meal_plan(), create_test_meal_plan()]
    
    mock_repo.find_meal_plans_by_user_id.return_value = plans
    
    result = await diet_service.get_meal_plans_by_user(user_id)
    
    mock_repo.find_meal_plans_by_user_id.assert_called_once_with(user_id)
    assert result == plans


@pytest.mark.asyncio
async def test_update_meal_plan_success(diet_service, mock_repo):
    plan_id = uuid4()
    plan = create_test_meal_plan(plan_id=plan_id)
    updated_plan = create_test_meal_plan(plan_id=plan_id)
    
    class MockMeal:
        def model_dump(self):
            return {"timing": "dinner", "food": "salmon and rice"}
    
    new_meals = [MockMeal()]
    
    mock_repo.find_meal_plan_by_id.return_value = plan
    mock_repo.update_meal_plan.return_value = updated_plan
    
    result = await diet_service.update_meal_plan(
        plan_id=plan_id,
        name="Updated Meal Plan",
        meals=new_meals
    )
    
    mock_repo.find_meal_plan_by_id.assert_called_once_with(plan_id)
    assert plan.name == "Updated Meal Plan"
    mock_repo.update_meal_plan.assert_called_once_with(plan)
    assert result == updated_plan


@pytest.mark.asyncio
async def test_update_meal_plan_empty_meals(diet_service, mock_repo):
    plan_id = uuid4()
    plan = create_test_meal_plan(plan_id=plan_id)
    
    mock_repo.find_meal_plan_by_id.return_value = plan
    
    with pytest.raises(ValueError, match="Meal Plan must have at least one meal"):
        await diet_service.update_meal_plan(
            plan_id=plan_id,
            meals=[]
        )


@pytest.mark.asyncio
async def test_update_meal_plan_partial(diet_service, mock_repo):
    plan_id = uuid4()
    plan = create_test_meal_plan(plan_id=plan_id)
    original_meals = plan.meals
    
    mock_repo.find_meal_plan_by_id.return_value = plan
    mock_repo.update_meal_plan.return_value = plan
    
    await diet_service.update_meal_plan(
        plan_id=plan_id,
        name="New Name Only"
    )
    
    assert plan.name == "New Name Only"
    assert plan.meals == original_meals  # Meals inchangés


@pytest.mark.asyncio
async def test_delete_meal_plan_success(diet_service, mock_repo):
    plan_id = uuid4()
    plan = create_test_meal_plan(plan_id=plan_id)
    
    mock_repo.find_meal_plan_by_id.return_value = plan
    
    await diet_service.delete_meal_plan(plan_id)
    
    mock_repo.find_meal_plan_by_id.assert_called_once_with(plan_id)
    mock_repo.delete_meal_plan.assert_called_once_with(plan_id)


@pytest.mark.asyncio
async def test_delete_meal_plan_not_found(diet_service, mock_repo):
    plan_id = uuid4()
    
    mock_repo.find_meal_plan_by_id.return_value = None
    
    with pytest.raises(NotFoundError, match=f"MealPlan {plan_id} not found"):
        await diet_service.delete_meal_plan(plan_id)