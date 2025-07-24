
import pytest
import uuid

@pytest.mark.asyncio
class TestGroupsScenario:
    admin_token: str = ""
    user_token: str = ""
    coach_token: str = ""
    user_uuid: str = ""
    coach_uuid: str = ""
    coach_group_uuid: str = ""
    admin_group_uuid: str = ""

    # 01 – création d’un user
    async def test_01_create_user_profile(self, client):
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
        TestGroupsScenario.user_token = body["token"]["access_token"]
        TestGroupsScenario.user_uuid = body["profile"]["id"]

    # 02 – création d’un coach (initialement role=["user"])
    async def test_02_create_coach_profile(self, client):
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
        TestGroupsScenario.coach_token = body["token"]["access_token"]
        TestGroupsScenario.coach_uuid = body["profile"]["id"]

    # 03 – login admin
    async def test_03_admin_login(self, client):
        r = await client.post(
            "/profiles/login",
            json={"email": "admin@mail.fr", "password": "123456789"}
        )
        assert r.status_code == 200
        TestGroupsScenario.admin_token = r.json()["access_token"]

    # 04 – promotion du coach → roles=["user","coach"]
    async def test_04_admin_promote_coach(self, client):
        update_data = {"roles": ["user", "coach"]}
        r = await client.patch(
            f"/profiles/{TestGroupsScenario.coach_uuid}/roles",
            json=update_data,
            headers={"Authorization": f"Bearer {TestGroupsScenario.admin_token}"}
        )
        assert r.status_code == 200
        roles = r.json()["roles"]
        assert "coach" in roles

    # 05 – relogin coach pour avoir le nouveau token
    async def test_05_coach_login_success(self, client):
        r = await client.post(
            "/profiles/login",
            json={"email": "coach@example.com", "password": "CoachPass123!"}
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        TestGroupsScenario.coach_token = data["access_token"]

    # 06 – coach crée un groupe
    async def test_06_coach_create_group(self, client):
        payload = {"name": "CoachGroup", "description": "Groupe du coach"}
        r = await client.post(
            "/groups",
            json=payload,
            headers={"Authorization": f"Bearer {TestGroupsScenario.coach_token}"}
        )
        assert r.status_code == 201
        grp = r.json()
        TestGroupsScenario.coach_group_uuid = grp["id"]
        assert grp["name"] == "CoachGroup"

    # 07 – coach lit un groupe inexistant → 404
    async def test_07_coach_get_group_not_found(self, client):
        fake = str(uuid.UUID(int=0))
        r = await client.get(
            f"/groups/{fake}",
            headers={"Authorization": f"Bearer {TestGroupsScenario.coach_token}"}
        )
        assert r.status_code == 404

    # 08 – coach lit son groupe → 200
    async def test_08_coach_get_group_success(self, client):
        r = await client.get(
            f"/groups/{TestGroupsScenario.coach_group_uuid}",
            headers={"Authorization": f"Bearer {TestGroupsScenario.coach_token}"}
        )
        assert r.status_code == 200
        assert r.json()["id"] == TestGroupsScenario.coach_group_uuid

    # 09 – coach met à jour son groupe → 200
    async def test_09_coach_update_group(self, client):
        update_data = {"name": "CoachGroupNew", "description": "Desc maj"}
        r = await client.patch(
            f"/groups/{TestGroupsScenario.coach_group_uuid}",
            json=update_data,
            headers={"Authorization": f"Bearer {TestGroupsScenario.coach_token}"}
        )
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "CoachGroupNew"

    # 10 – user tente de mettre à jour le groupe du coach → 403
    async def test_10_user_update_group_forbidden(self, client):
        update_data = {"name": "Hack"}
        r = await client.patch(
            f"/groups/{TestGroupsScenario.coach_group_uuid}",
            json=update_data,
            headers={"Authorization": f"Bearer {TestGroupsScenario.user_token}"}
        )
        assert r.status_code == 403

    # 11 – admin met à jour le groupe du coach → 200
    async def test_11_admin_update_group(self, client):
        update_data = {"description": "Admin update"}
        r = await client.patch(
            f"/groups/{TestGroupsScenario.coach_group_uuid}",
            json=update_data,
            headers={"Authorization": f"Bearer {TestGroupsScenario.admin_token}"}
        )
        assert r.status_code == 200
        assert r.json()["description"] == "Admin update"

    # 12 – user avec token invalide lit la liste → 401
    async def test_12_user_get_groups_invalid_token(self, client):
        r = await client.get(
            "/groups",
            headers={"Authorization": "Bearer invalidtoken"}
        )
        assert r.status_code == 401

    # 13 – user lit tous les groupes → 200
    async def test_13_user_list_groups(self, client):
        r = await client.get(
            "/groups",
            headers={"Authorization": f"Bearer {TestGroupsScenario.user_token}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # 14 – user tente de créer un groupe → 403
    async def test_14_user_create_group_forbidden(self, client):
        payload = {"name": "UserGroup", "description": "Desc"}
        r = await client.post(
            "/groups",
            json=payload,
            headers={"Authorization": f"Bearer {TestGroupsScenario.user_token}"}
        )
        assert r.status_code == 403

    # 15 – admin crée un groupe
    async def test_15_admin_create_group(self, client):
        payload = {"name": "AdminGroup", "description": "Groupe admin"}
        r = await client.post(
            "/groups",
            json=payload,
            headers={"Authorization": f"Bearer {TestGroupsScenario.admin_token}"}
        )
        assert r.status_code == 201
        grp = r.json()
        TestGroupsScenario.admin_group_uuid = grp["id"]

    # 16 – coach supprime le groupe admin → 403
    async def test_16_coach_delete_admin_group_forbidden(self, client):
        r = await client.delete(
            f"/groups/{TestGroupsScenario.admin_group_uuid}",
            headers={"Authorization": f"Bearer {TestGroupsScenario.coach_token}"}
        )
        assert r.status_code == 403

    # 17 – admin supprime son propre groupe → 204
    async def test_17_admin_delete_admin_group_success(self, client):
        r = await client.delete(
            f"/groups/{TestGroupsScenario.admin_group_uuid}",
            headers={"Authorization": f"Bearer {TestGroupsScenario.admin_token}"}
        )
        assert r.status_code == 204

    # 18 – coach ajoute l’utilisateur au groupe → 204
    async def test_18_coach_add_user_to_group(self, client):
        r = await client.post(
            f"/groups/{TestGroupsScenario.coach_group_uuid}/members/{TestGroupsScenario.user_uuid}",
            headers={"Authorization": f"Bearer {TestGroupsScenario.coach_token}"}
        )
        assert r.status_code == 204

    # 19 – admin retire l’utilisateur du groupe → 204
    async def test_19_admin_remove_user_from_group(self, client):
        r = await client.delete(
            f"/groups/{TestGroupsScenario.coach_group_uuid}/members/{TestGroupsScenario.user_uuid}",
            headers={"Authorization": f"Bearer {TestGroupsScenario.admin_token}"}
        )
        assert r.status_code == 204, f"Failed to add member: { r.text }"


    # 20 – admin ré-ajoute l’utilisateur → 204
    async def test_20_admin_add_user_to_group(self, client):
        r = await client.post(
            f"/groups/{TestGroupsScenario.coach_group_uuid}/members/{TestGroupsScenario.user_uuid}",
            headers={"Authorization": f"Bearer {TestGroupsScenario.admin_token}"}
        )
        assert r.status_code == 204

    # 21 – user tente de lister les membres → 403
    async def test_21_user_list_members_forbidden(self, client):
        r = await client.get(
            f"/groups/{TestGroupsScenario.coach_group_uuid}/members",
            headers={"Authorization": f"Bearer {TestGroupsScenario.user_token}"}
        )
        assert r.status_code == 403

    # 22 – admin liste les membres → 200
    async def test_22_admin_list_members(self, client):
        r = await client.get(
            f"/groups/{TestGroupsScenario.coach_group_uuid}/members",
            headers={"Authorization": f"Bearer {TestGroupsScenario.admin_token}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # 23 – coach liste les membres → 200
    async def test_23_coach_list_members(self, client):
        r = await client.get(
            f"/groups/{TestGroupsScenario.coach_group_uuid}/members",
            headers={"Authorization": f"Bearer {TestGroupsScenario.coach_token}"}
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    # 24 – user liste les groupes du coach (owner) → 200
    async def test_24_user_list_owner_groups(self, client):
        r = await client.get(
            f"/groups/owner/{TestGroupsScenario.coach_uuid}",
            headers={"Authorization": f"Bearer {TestGroupsScenario.user_token}"}
        )
        assert r.status_code == 200
        groups = r.json()
        assert any(g["id"] == TestGroupsScenario.coach_group_uuid for g in groups)

    # 25 – user quitte le groupe → 204
    async def test_25_user_leave_group_success(self, client):
        r = await client.delete(
            f"/groups/{TestGroupsScenario.coach_group_uuid}/leave",
            headers={"Authorization": f"Bearer {TestGroupsScenario.user_token}"}
        )
        assert r.status_code == 204

    # 26 – user quitte à nouveau → 404
    async def test_26_user_leave_group_not_found(self, client):
        r = await client.delete(
            f"/groups/{TestGroupsScenario.coach_group_uuid}/leave",
            headers={"Authorization": f"Bearer {TestGroupsScenario.user_token}"}
        )
        assert r.status_code == 404


# créer un user/ créer un coach (user)
# admin update role coach add coach
# coach login for add new coach token
# coach créate a groups
# coach try to get one group wrong uuid
# coach try to get one group good uuid
# coach update group 200
# user update group 403
# admin update group 200
# user wrong token get groups 401
#  user get groups 200
# user create groups 403
#  admin create group 200
#  coach delte admin group 403
# admin delete admin group 200
# coach add user member to group 200
# admin remove user member to group 200
#  admin add user member to coac group 200
#  user list member of group 403
#  admin list member of group 200
#  coach list member of group 200
# user list owner groups (all coach group) 200
# user leave groups 204
#  user leave groups not found 404