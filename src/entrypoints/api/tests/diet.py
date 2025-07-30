import pytest

@pytest.mark.asyncio
class TestDietScenario:
    
    # create new user (user3) not in team
    async def test_01_create_new_user_not_in_team(self, client, test_state):
        payload = { 
            "email": "user3@example.com",
            "password": "Secret123!",
            "confirm_password": "Secret123!"
        }
        r = await client.post(
            "/profiles",
            json=payload,
        )
        assert r.status_code == 201
        body = r.json()
        test_state['user3_token'] = body["token"]["access_token"]
        test_state['user3_uuid'] = body["profile"]["id"]
    
    # coach create diet for user not in team -> 403
    async def test_02_coach_create_diet_for_user_forbidden_not_in_team(self, client, test_state):
        payload = {"name": "Diet1", "description": "Test Diet"}
        r = await client.post(
            f"/diets/{test_state['user3_uuid']}",  # user3 n'est pas dans l'équipe du coach
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 403

    # coach create diet for user in team -> 201
    async def test_03_coach_create_diet_for_user(self, client, test_state):
        payload = {"name": "Diet1", "description": "Test Diet"}
        r = await client.post(
            f"/diets/{test_state['user_uuid']}",  # user est dans l'équipe du coach
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['diet_id'] = body["id"]

    # user create diet -> 403
    async def test_04_user_create_diet_forbidden(self, client, test_state):
        payload = {"name": "Diet2", "description": "Test Diet 2"}
        r = await client.post(
            f"/diets/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # coach update diet -> 200
    async def test_05_coach_update_diet(self, client, test_state):
        payload = {"name": "Diet1 Updated", "description": "Test Diet Updated"}
        r = await client.patch(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200

    # admin create diet for user -> 201
    async def test_06_admin_create_diet_for_user(self, client, test_state):
        payload = {"name": "AdminDiet", "description": "Admin Test Diet"}
        r = await client.post(
            f"/diets/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['admin_diet_id'] = body["id"]

    # admin update diet -> 200
    async def test_07_admin_update_diet(self, client, test_state):
        payload = {"name": "AdminDiet Updated", "description": "Admin Test Diet Updated"}
        r = await client.patch(
            f"/diets/{test_state['admin_diet_id']}/user/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200

    # coach update admin diet -> 200
    async def test_08_coach_update_admin_diet(self, client, test_state):
        payload = {"name": "AdminDiet Coach Update", "description": "Coach trying to update admin diet"}
        r = await client.patch(
            f"/diets/{test_state['admin_diet_id']}/user/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200

    # coach get user diets -> 200
    async def test_09_coach_get_user_diets(self, client, test_state):
        r = await client.get(
            f"/diets/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # admin get user diets -> 200
    async def test_10_admin_get_user_diets(self, client, test_state):
        r = await client.get(
            f"/diets/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # user get user diets -> 403
    async def test_11_user_get_user_diets_forbidden(self, client, test_state):
        r = await client.get(
            f"/diets/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # user get mine diets -> 200
    async def test_12_user_get_mine_diets(self, client, test_state):
        r = await client.get(
            "/diets/mine",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # coach get mine diets (should be empty) -> 200
    async def test_13_coach_get_mine_diets(self, client, test_state):
        r = await client.get(
            "/diets/mine",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        # Should be empty since coach doesn't own diets for himself
        assert len(r.json()) == 0

    # MACRO PLAN TESTS

    # coach create macroplan in diet -> 201
    async def test_14_coach_create_macroplan_in_diet(self, client, test_state):
        payload = {
            "name": "MacroPlan1",
            "carbohydrates": 250.0,
            "lipids": 80.0,
            "protein": 120.0,
            "fiber": 35.0,
            "water": 2.5,
            "kilocalorie": 2000.0
        }
        r = await client.post(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/macro_plans",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['macro_plan_id'] = body["id"]

    # admin create macroplan in diet -> 201
    async def test_15_admin_create_macroplan_in_diet(self, client, test_state):
        payload = {
            "name": "AdminMacroPlan",
            "carbohydrates": 300.0,
            "lipids": 90.0,
            "protein": 150.0,
            "fiber": 40.0,
            "water": 3.0,
            "kilocalorie": 2200.0
        }
        r = await client.post(
            f"/diets/{test_state['admin_diet_id']}/user/{test_state['user_uuid']}/macro_plans",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['admin_macro_plan_id'] = body["id"]

    # user create macroplan -> 403
    async def test_16_user_create_macroplan_forbidden(self, client, test_state):
        payload = {
            "name": "UserMacroPlan",
            "carbohydrates": 200.0,
            "lipids": 70.0,
            "protein": 100.0,
            "fiber": 30.0,
            "water": 2.0,
            "kilocalorie": 1800.0
        }
        r = await client.post(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/macro_plans",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # coach update macroplan -> 200
    async def test_17_coach_update_macroplan(self, client, test_state):
        payload = {
            "name": "MacroPlan1 Updated",
            "carbohydrates": 260.0,
            "kilocalorie": 2100.0
        }
        r = await client.patch(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/macro_plans/{test_state['macro_plan_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200

    # admin update macroplan -> 200
    async def test_18_admin_update_macroplan(self, client, test_state):
        payload = {
            "name": "AdminMacroPlan Updated",
            "protein": 160.0
        }
        r = await client.patch(
            f"/diets/{test_state['admin_diet_id']}/user/{test_state['user_uuid']}/macro_plans/{test_state['admin_macro_plan_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200

    # user update macroplan -> 403
    async def test_19_user_update_macroplan_forbidden(self, client, test_state):
        payload = {"name": "User Update Attempt"}
        r = await client.patch(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/macro_plans/{test_state['macro_plan_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # user get mine macroplans -> 200
    async def test_20_user_get_mine_macroplans(self, client, test_state):
        r = await client.get(
            "/diets/macro_plans/mine",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # user get all macroplans by diet -> 200
    async def test_21_user_get_all_macroplans_by_diet(self, client, test_state):
        r = await client.get(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/macro_plans",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # coach get macroplans by diet -> 200
    async def test_22_coach_get_macroplans_by_diet(self, client, test_state):
        r = await client.get(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/macro_plans",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # admin get specific macroplan -> 200
    async def test_23_admin_get_specific_macroplan(self, client, test_state):
        r = await client.get(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/macro_plans/{test_state['macro_plan_id']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200

    # MEAL PLAN TESTS

    # coach create mealplan in diet -> 201
    async def test_24_coach_create_mealplan_in_diet(self, client, test_state):
        payload = {
            "name": "MealPlan1",
            "meals": [
                {"timing": "breakfast", "food": "oatmeal with fruits"},
                {"timing": "lunch", "food": "chicken with rice"},
                {"timing": "dinner", "food": "salmon with vegetables"}
            ]
        }
        r = await client.post(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/meal_plans",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['meal_plan_id'] = body["id"]

    # admin create mealplan in diet -> 201
    async def test_25_admin_create_mealplan_in_diet(self, client, test_state):
        payload = {
            "name": "AdminMealPlan",
            "meals": [
                {"timing": "breakfast", "food": "protein shake"},
                {"timing": "snack", "food": "nuts and fruits"}
            ]
        }
        r = await client.post(
            f"/diets/{test_state['admin_diet_id']}/user/{test_state['user_uuid']}/meal_plans",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['admin_meal_plan_id'] = body["id"]

    # user create mealplan -> 403
    async def test_26_user_create_mealplan_forbidden(self, client, test_state):
        payload = {
            "name": "UserMealPlan",
            "meals": [{"timing": "breakfast", "food": "cereal"}]
        }
        r = await client.post(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/meal_plans",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # coach update mealplan -> 200
    async def test_27_coach_update_mealplan(self, client, test_state):
        payload = {
            "name": "MealPlan1 Updated",
            "meals": [
                {"timing": "breakfast", "food": "greek yogurt with berries"},
                {"timing": "lunch", "food": "turkey sandwich"}
            ]
        }
        r = await client.patch(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/meal_plans/{test_state['meal_plan_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200

    # admin update mealplan -> 200
    async def test_28_admin_update_mealplan(self, client, test_state):
        payload = {
            "name": "AdminMealPlan Updated"
        }
        r = await client.patch(
            f"/diets/{test_state['admin_diet_id']}/user/{test_state['user_uuid']}/meal_plans/{test_state['admin_meal_plan_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200

    # user update mealplan -> 403
    async def test_29_user_update_mealplan_forbidden(self, client, test_state):
        payload = {"name": "User Update Attempt"}
        r = await client.patch(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/meal_plans/{test_state['meal_plan_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # user get mine mealplans -> 200
    async def test_30_user_get_mine_mealplans(self, client, test_state):
        r = await client.get(
            "/diets/meal_plans/mine",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # user get all mealplans by diet -> 200
    async def test_31_user_get_all_mealplans_by_diet(self, client, test_state):
        r = await client.get(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/meal_plans",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # coach get mealplans by diet -> 200
    async def test_32_coach_get_mealplans_by_diet(self, client, test_state):
        r = await client.get(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/meal_plans",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # admin get specific mealplan -> 200
    async def test_33_admin_get_specific_mealplan(self, client, test_state):
        r = await client.get(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/meal_plans/{test_state['meal_plan_id']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200

    # DELETE TESTS

    # user delete diet -> 403
    async def test_34_user_delete_diet_forbidden(self, client, test_state):
        r = await client.delete(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # admin delete macroplan -> 204
    async def test_35_admin_delete_macroplan(self, client, test_state):
        r = await client.delete(
            f"/diets/{test_state['admin_diet_id']}/user/{test_state['user_uuid']}/macro_plans/{test_state['admin_macro_plan_id']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 204

    # coach delete macroplan -> 204
    async def test_36_coach_delete_macroplan(self, client, test_state):
        r = await client.delete(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/macro_plans/{test_state['macro_plan_id']}",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 204

    # admin delete mealplan -> 204
    async def test_37_admin_delete_mealplan(self, client, test_state):
        r = await client.delete(
            f"/diets/{test_state['admin_diet_id']}/user/{test_state['user_uuid']}/meal_plans/{test_state['admin_meal_plan_id']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 204

    # coach delete mealplan -> 204
    async def test_38_coach_delete_mealplan(self, client, test_state):
        r = await client.delete(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}/meal_plans/{test_state['meal_plan_id']}",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 204

    # admin delete coach diet -> 204
    async def test_39_admin_delete_coach_diet(self, client, test_state):
        r = await client.delete(
            f"/diets/{test_state['diet_id']}/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 204

    # admin delete admin diet -> 204
    async def test_40_admin_delete_admin_diet(self, client, test_state):
        r = await client.delete(
            f"/diets/{test_state['admin_diet_id']}/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 204

    # Tests additionnels pour une meilleure couverture

    # user3 access user1 diets -> 403
    async def test_41_user3_access_user1_diets_forbidden(self, client, test_state):
        # Create a diet first for testing
        payload = {"name": "TestDiet", "description": "Test"}
        r = await client.post(
            f"/diets/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 201
        
        # user3 tries to access user1's diets
        r = await client.get(
            f"/diets/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['user3_token']}"}
        )
        assert r.status_code == 403

    # Test error cases
    
    # create diet with invalid data -> 400 or 422
    async def test_42_create_diet_invalid_data(self, client, test_state):
        payload = {"name": ""}  # Empty name should fail
        r = await client.post(
            f"/diets/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        # Depending on validation, this might be 400 or 422
        assert r.status_code in [400, 422]

    # update non-existent diet -> 404
    async def test_43_update_nonexistent_diet(self, client, test_state):
        from uuid import uuid4
        fake_diet_id = str(uuid4())
        payload = {"name": "Updated"}
        r = await client.patch(
            f"/diets/{fake_diet_id}/user/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 404

    # delete non-existent diet -> 404
    async def test_44_delete_nonexistent_diet(self, client, test_state):
        from uuid import uuid4
        fake_diet_id = str(uuid4())
        r = await client.delete(
            f"/diets/{fake_diet_id}/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 404