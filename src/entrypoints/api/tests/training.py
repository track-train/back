# coach create an group → 201
# coach create training for user -> 403 
# coach add user to group → 200
# coach create training for user -> 201
# user create trainging for user -> 403
# coach update training for user -> 200
# admin update training for user -> 200
# user create tasks for training -> 403
# coach create tasks for training -> 201
# admin create tasks for training -> 201
# coach get all trainings for user -> 200
# admin get all trainings for user -> 200
# user get all trainings for user -> 403
# user get all mine trainings -> 200
# user get all mine tasks -> 200
# user update task -> 403
# admin update task -> 200
# coach update task -> 200
# create new user (user2) -> 200
# user create validation for task -> 200
# user2 create validation for task -> 403
# user get all validations for task -> 200
# coach get all validations for task -> 200
# admin get all validations for task -> 200
# user2 get all validations for task -> 403
# user get all validations for training -> 200
# coach get all validations for training -> 200
# admin get all validations for training -> 200
# user2 get all validations for training -> 403
# user delete validation for task -> 200
# coach delete validation for task -> 403
# admin delete validation for task -> 200


import pytest

@pytest.mark.asyncio
class TestTrainingScenario:
    
    # Setup: ensure all required tokens exist
    async def test_00_setup_prerequisites(self, client, test_state):
        # Setup user if not exists
        if 'user_token' not in test_state:
            payload = {
                "email": "alice@example.com",
                "password": "Secret123!",
                "confirm_password": "Secret123!",
                "name": "Alice",
                "sex": "F",
                "age": 28
            }
            r = await client.post("/profiles", json=payload)
            assert r.status_code == 201
            body = r.json()
            test_state["user_token"] = body["token"]["access_token"]
            test_state["user_uuid"] = body["profile"]["id"]

        # Setup coach if not exists
        if 'coach_token' not in test_state:
            payload = {
                "email": "coach@example.com",
                "password": "CoachPass123!",
                "confirm_password": "CoachPass123!",
                "name": "Coach",
                "sex": "M",
                "age": 35
            }
            r = await client.post("/profiles", json=payload)
            assert r.status_code == 201
            body = r.json()
            test_state["coach_token"] = body["token"]["access_token"]
            test_state["coach_uuid"] = body["profile"]["id"]

        # Setup admin if not exists
        if 'admin_token' not in test_state:
            r = await client.post(
                "/profiles/login",
                json={"email": "admin@mail.fr", "password": "123456789"}
            )
            assert r.status_code == 200
            test_state["admin_token"] = r.json()["access_token"]

        # Promote coach if not done
        if 'coach_promoted' not in test_state:
            update_data = {"roles": ["user", "coach"]}
            r = await client.patch(
                f"/profiles/{test_state['coach_uuid']}/roles",
                json=update_data,
                headers={"Authorization": f"Bearer {test_state['admin_token']}"}
            )
            assert r.status_code == 200
            roles = r.json()["roles"]
            assert "coach" in roles
            test_state['coach_promoted'] = True

        # Re-login coach to get new token with coach role
        if 'coach_relogged' not in test_state:
            r = await client.post(
                "/profiles/login",
                json={"email": "coach@example.com", "password": "CoachPass123!"}
            )
            assert r.status_code == 200
            test_state["coach_token"] = r.json()["access_token"]
            test_state['coach_relogged'] = True

# coach create an group → 201
    async def test_01_coach_create_group(self, client, test_state):
        payload = {"name": "Group1", "description": "Test Group"}
        r = await client.post(
            "/groups",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['group_id'] = body["id"]
# coach create training for user -> 403 
    async def test_02_coach_create_training_for_user_forbidden(self, client, test_state):
        payload = {"name": "Training1", "description": "Test Training"}
        r = await client.post(
            f"/trainings/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 403
# coach add user to group → 204
    async def test_03_coach_add_user_to_group(self, client, test_state):
        r = await client.post(
            f"/groups/{test_state['group_id']}/members/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 204
# coach create training for user -> 201
    async def test_04_coach_create_training_for_user(self, client, test_state):
        payload = {"name": "Training1", "description": "Test Training"}
        r = await client.post(
            f"/trainings/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['training_id'] = body["id"]
# user create trainging for user -> 403
    async def test_05_user_create_training_for_user_forbidden(self, client, test_state):
        payload = {"name": "Training1", "description": "Test Training"}
        r = await client.post(
            f"/trainings/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403
# coach update training for user -> 200
    async def test_06_coach_update_training_for_user(self, client, test_state):
        payload = {"name": "Training1 Updated", "description": "Test Training Updated"}
        r = await client.patch(
            f"/trainings/{test_state['training_id']}/user/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
# admin update training for user -> 200
    async def test_07_admin_update_training_for_user(self, client, test_state):
        payload = {"name": "Training1 Updated", "description": "Test Training Updated"}
        r = await client.patch(
            f"/trainings/{test_state['training_id']}/user/{test_state['user_uuid']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200
# user create tasks for training -> 403
    async def test_08_user_create_tasks_for_training_forbidden(self, client, test_state):
        payload = {
            "exercise_name": "Squat",
            "rest_time": 60,
            "repetitions": 10,
            "set_number": 3,
            "method": "classic",
            "rir": 2,
        }
        r = await client.post(
            f"/trainings/{test_state['training_id']}/user/{test_state['user_uuid']}/tasks",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403
# coach create tasks for training -> 201
    async def test_09_coach_create_tasks_for_training(self, client, test_state):
        payload = {
            "exercise_name": "Squat",
            "rest_time": 60,
            "repetitions": 10,
            "set_number": 3,
            "method": "classic",
            "rir": 2,
        }
        r = await client.post(
            f"/trainings/{test_state['training_id']}/user/{test_state['user_uuid']}/tasks",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 201
# admin create tasks for training -> 201
    async def test_10_admin_create_tasks_for_training(self, client, test_state):
        payload = {
            "exercise_name": "Squat",
            "rest_time": 60,
            "repetitions": 10,
            "set_number": 3,
            "method": "classic",
            "rir": 2,
        }
        r = await client.post(
            f"/trainings/{test_state['training_id']}/user/{test_state['user_uuid']}/tasks",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['task_id'] = body["id"]
# coach get all trainings for user -> 200
    async def test_11_coach_get_all_trainings_for_user(self, client, test_state):
        r = await client.get(
            f"/trainings/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
# admin get all trainings for user -> 200
    async def test_12_admin_get_all_trainings_for_user(self, client, test_state):
        r = await client.get(
            f"/trainings/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
# user get all trainings for user -> 403
    async def test_13_user_get_all_trainings_for_user_forbidden(self, client, test_state):
        r = await client.get(
            f"/trainings/user/{test_state['user_uuid']}",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403
# user get all mine trainings -> 200
    async def test_14_user_get_all_mine_trainings(self, client, test_state):
        r = await client.get(
            "/trainings/mine",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

# user update task -> 403
    async def test_16_user_update_task_forbidden(self, client, test_state):
        payload = {"name": "Task1 Updated", "description": "Test Task Updated"}
        r = await client.patch(
            f"/trainings/{test_state['training_id']}/user/{test_state['user_uuid']}/tasks/{test_state['task_id']}",  # ✅ Ajout de /trainings
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403
# admin update task -> 200
    async def test_17_admin_update_task(self, client, test_state):
        payload = {"name": "Task1 Updated", "description": "Test Task Updated"}
        r = await client.patch(
            f"/trainings/{test_state['training_id']}/user/{test_state['user_uuid']}/tasks/{test_state['task_id']}",  # ✅ Ajout de /trainings
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200
# coach update task -> 200
    async def test_18_coach_update_task(self, client, test_state):
        payload = {"name": "Task1 Updated", "description": "Test Task Updated"}
        r = await client.patch(
            f"/trainings/{test_state['training_id']}/user/{test_state['user_uuid']}/tasks/{test_state['task_id']}",  # ✅ Ajout de /trainings
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
# create new user (user2) -> 200
    async def test_19_create_new_user(self, client, test_state):
        payload = { 
            "email": "bob@example.com",
            "password": "Secret123!",
            "confirm_password": "Secret123!"}
        r = await client.post(
            "/profiles",
            json=payload,
        )
        assert r.status_code == 201
        body = r.json()
        test_state['user2_token'] = body["token"]["access_token"]
        test_state['user2_uuid'] = body["profile"]["id"]
# user create validation for task -> 200
    async def test_20_user_create_validation_for_task(self, client, test_state):
        payload = {"comment": "Good job!", "score": 5}
        r = await client.post(
            f"/trainings/{test_state['training_id']}/tasks/{test_state['task_id']}/validations",  # ✅ Ajout de /trainings
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['validation_uuid'] = body["id"]
# user2 create validation for task -> 403
    async def test_21_user2_create_validation_for_task_forbidden(self, client, test_state):
        payload = {"comment": "Good job!", "score": 5}
        r = await client.post(
            f"trainings/{test_state['training_id']}/tasks/{test_state['task_id']}/validations",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user2_token']}"}
        )
        assert r.status_code == 403

# user get all validations for task -> 200
    async def test_22_user_get_all_validations_for_task(self, client, test_state):
        r = await client.get(
            f"trainings/{test_state['training_id']}/tasks/{test_state['task_id']}/validations",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
# coach get all validations for task -> 200
    async def test_23_coach_get_all_validations_for_task(self, client, test_state):
        r = await client.get(
            f"trainings/{test_state['training_id']}/tasks/{test_state['task_id']}/validations",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
# admin get all validations for task -> 200
    async def test_24_admin_get_all_validations_for_task(self, client, test_state):
        r = await client.get(
            f"trainings/{test_state['training_id']}/tasks/{test_state['task_id']}/validations",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
# user2 get all validations for task -> 403
    async def test_25_user2_get_all_validations_for_task_forbidden(self, client, test_state):
        r = await client.get(
            f"trainings/{test_state['training_id']}/tasks/{test_state['task_id']}/validations",
            headers={"Authorization": f"Bearer {test_state['user2_token']}"}
        )
        assert r.status_code == 403
# user get all validations for training -> 200
    async def test_26_user_get_all_validations_for_training(self, client, test_state):
        r = await client.get(
            f"trainings/{test_state['training_id']}/validations",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
# coach get all validations for training -> 200
    async def test_27_coach_get_all_validations_for_training(self, client, test_state):
        r = await client.get(
            f"/trainings/{test_state['training_id']}/validations",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
# admin get all validations for training -> 200
    async def test_28_admin_get_all_validations_for_training(self, client, test_state):
        r = await client.get(
            f"/trainings/{test_state['training_id']}/validations",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)
# user2 get all validations for training -> 403
    async def test_29_user2_get_all_validations_for_training_forbidden(self, client, test_state):
        r = await client.get(
            f"/trainings/{test_state['training_id']}/validations",
            headers={"Authorization": f"Bearer {test_state['user2_token']}"}
        )
        assert r.status_code == 403
# user delete validation for task -> 204
    async def test_30_user_delete_validation_for_task(self, client, test_state):
        r = await client.delete(
            f"trainings/{test_state['training_id']}/tasks/{test_state['task_id']}/validations/{test_state['validation_uuid']}",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 204
# coach delete validation for task -> 403
    async def test_31_coach_delete_validation_for_task_forbidden(self, client, test_state):
        r = await client.delete(
            f"/trainings/{test_state['training_id']}/tasks/{test_state['task_id']}/validations/{test_state['validation_uuid']}",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 403
# admin delete validation for task -> 404
    async def test_32_admin_delete_validation_for_task_not_found(self, client, test_state):
        r = await client.delete(
            f"/trainings/{test_state['training_id']}/tasks/{test_state['task_id']}/validations/{test_state['validation_uuid']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 404
