import pytest


@pytest.mark.asyncio
class TestExercisesScenario:

    # 05 – user tente de créer un exercice → 403
    async def test_01_user_create_exercise_forbidden(self, client, test_state):
        payload = {"name": "Exo1", "description": "desc exo1"}
        r = await client.post(
            "/exercises",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # 06 – coach crée un exercice → 201
    async def test_02_coach_create_exercise(self, client, test_state):
        payload = {"name": "ExoCoach", "description": "desc coach"}
        r = await client.post(
            "/exercises",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['coach_exercise_id'] = body["id"]

    # 07 – admin crée un exercice → 201
    async def test_03_admin_create_exercise(self, client, test_state):
        payload = {"name": "ExoAdmin", "description": "desc admin"}
        r = await client.post(
            "/exercises",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['exercise_id'] = body["id"]

    # 08 – user tente de modifier exercice → 403
    async def test_04_user_update_exercise_forbidden(self, client, test_state):
        payload = {"name": "Hacked", "description": "Hacked desc"}
        r = await client.patch(
            f"/exercises/{test_state['coach_exercise_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # 09 – admin donne rôle coach à user, user tente update → 403; admin retire coach à user
    async def test_05_admin_update_roles_user_and_try_update_exercise(self, client, test_state):
        # Ajoute rôle coach à user
        r = await client.patch(
            f"/profiles/{test_state['user_uuid']}/roles",
            json={"roles": ["user", "coach"]},
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200
        # User tente update (il n'est pas owner)
        payload = {"name": "Hacked2", "description": "Hacked desc2"}
        r = await client.patch(
            f"/exercises/{test_state['coach_exercise_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403
        # Admin retire coach à user
        r = await client.patch(
            f"/profiles/{test_state['user_uuid']}/roles",
            json={"roles": ["user"]},
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200

    # 10 – admin update exercice → 200
    async def test_06_admin_update_exercise(self, client, test_state):
        payload = {"name": "AdminUpdate", "description": "Admin modif"}
        r = await client.patch(
            f"/exercises/{test_state['coach_exercise_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 200

    # 11 – coach update exercice → 200
    async def test_07_coach_update_exercise(self, client, test_state):
        payload = {"name": "CoachUpdate", "description": "Coach modif"}
        r = await client.patch(
            f"/exercises/{test_state['coach_exercise_id']}",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200

    # 12 – user get exercises → 200
    async def test_08_user_get_exercises(self, client, test_state):
        r = await client.get(
            "/exercises",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # 13 – user get one exercise → 200
    async def test_09_user_get_one_exercise(self, client, test_state):
        r = await client.get(
            f"/exercises/{test_state['coach_exercise_id']}",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 200

    # 14 – user get all mine exercises → 403
    async def test_10_user_get_mine_exercises_forbidden(self, client, test_state):
        r = await client.get(
            "/exercises/mine",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # 15 – coach get all mine exercises → 200
    async def test_11_coach_get_mine_exercises(self, client, test_state):
        r = await client.get(
            "/exercises/mine",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # 16 – admin supprime exercice coach → 204
    async def test_12_admin_delete_coach_exercise(self, client, test_state):
        r = await client.delete(
            f"/exercises/{test_state['coach_exercise_id']}",
            headers={"Authorization": f"Bearer {test_state['admin_token']}"}
        )
        assert r.status_code == 204

    # 17 – coach crée un exercice → 201
    async def test_13_coach_create_exercise(self, client, test_state):
        payload = {"name": "ExoCoach2", "description": "desc coach 2"}
        r = await client.post(
            "/exercises",
            json=payload,
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 201
        body = r.json()
        test_state['coach_exercise_id'] = body["id"]

    # 18 – user delete coach exercise → 403
    async def test_14_user_delete_coach_exercise_forbidden(self, client, test_state):
        r = await client.delete(
            f"/exercises/{test_state['coach_exercise_id']}",
            headers={"Authorization": f"Bearer {test_state['user_token']}"}
        )
        assert r.status_code == 403

    # 19 – coach delete exercise → 204
    async def test_15_coach_delete_exercise(self, client, test_state):
        r = await client.delete(
            f"/exercises/{test_state['coach_exercise_id']}",
            headers={"Authorization": f"Bearer {test_state['coach_token']}"}
        )
        assert r.status_code == 204



# create new user profile
# create new coach profile
# admin update roles for coach to coach
# user try to create a exercise 403
# coach create exercise 201
# admin creatre exercise 201
# user try to update exercise 403
# admin update user to coach and user try to update exercise 403, admin remove coach role from user
# admin update exercise 200
# coach update exercise 200
# user get exercises 200
# user get one exercise 200
# user get all mine exercises 403
# coach get all mine exercises 200
# admin delete coach exercise 204
# coach create exercise 201
# user delete coach exercise 403
# coach delete exercise 204