import pytest
import uuid

@pytest.mark.asyncio
class TestProfilesScenario:
    admin_token = ""
    user_token = ""
    coach_token = ""
    user_uuid = ""
    coach_uuid = ""

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
        self.__class__.user_token = body["token"]["access_token"]
        self.__class__.user_uuid = body["profile"]["id"]
        assert body["profile"]["roles"] == ["user"]

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
        self.__class__.coach_token = body["token"]["access_token"]
        self.__class__.coach_uuid = body["profile"]["id"]
        assert body["profile"]["roles"] == ["user"]

    async def test_03_admin_login(self, client):
        r = await client.post(
            "/profiles/login",
            json={"email": "admin@mail.fr", "password": "123456789"}
        )
        assert r.status_code == 200
        self.__class__.admin_token = r.json()["access_token"]

    async def test_04_admin_promote_coach(self, client):
        update_data = {"roles": ["user", "coach"]}
        r = await client.patch(
            f"/profiles/{self.__class__.coach_uuid}/roles",
            json=update_data,
            headers={"Authorization": f"Bearer {self.__class__.admin_token}"}
        )
        assert r.status_code == 200
        roles = r.json()["roles"]
        assert "coach" in roles

    async def test_05_coach_cannot_update_roles(self, client):
        update_data = {"roles": ["admin"]}
        r = await client.patch(
            f"/profiles/{self.__class__.user_uuid}/roles",
            json=update_data,
            headers={"Authorization": f"Bearer {self.__class__.coach_token}"}
        )
        assert r.status_code == 403

    async def test_06_user_cannot_update_roles(self, client):
        update_data = {"roles": ["admin"]}
        r = await client.patch(
            f"/profiles/{self.__class__.user_uuid}/roles",
            json=update_data,
            headers={"Authorization": f"Bearer {self.__class__.user_token}"}
        )
        assert r.status_code == 403

    async def test_07_create_duplicate_user_profile_returns_400(self, client):
        payload = {
            "email": "alice@example.com",
            "password": "Secret123!",
            "confirm_password": "Secret123!",
            "name": "Alice Dup"
        }
        r = await client.post("/profiles", json=payload)
        assert r.status_code == 400
        assert "already exists" in r.json()["detail"].lower()

    async def test_08_coach_cannot_update_user_profile(self, client):
        update_data = {"name": "HackerName"}
        r = await client.patch(
            f"/profiles/{self.__class__.user_uuid}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.__class__.coach_token}"}
        )
        assert r.status_code == 403

    async def test_09_admin_can_update_user_profile(self, client):
        update_data = {"name": "AdminUpdatedName"}
        r = await client.patch(
            f"/profiles/{self.__class__.user_uuid}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.__class__.admin_token}"}
        )
        assert r.status_code == 200
        assert r.json()["name"] == "AdminUpdatedName"

    async def test_10_user_can_update_own_profile(self, client):
        update_data = {"name": "UserUpdatedName"}
        r = await client.patch(
            f"/profiles/{self.__class__.user_uuid}",
            json=update_data,
            headers={"Authorization": f"Bearer {self.__class__.user_token}"}
        )
        assert r.status_code == 200
        assert r.json()["name"] == "UserUpdatedName"

    async def test_11_coach_get_me_success(self, client):
        r = await client.get(
            "/profiles/me",
            headers={"Authorization": f"Bearer {self.__class__.coach_token}"}
        )
        assert r.status_code == 200
        assert r.json()["email"] == "coach@example.com"

    async def test_12_coach_get_me_with_invalid_token(self, client):
        r = await client.get(
            "/profiles/me",
            headers={"Authorization": "Bearer invalidtoken"}
        )
        assert r.status_code == 401

    async def test_13_public_get_coaches(self, client):
        r = await client.get("/profiles/coachs")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    async def test_14_user_cannot_get_all_users(self, client):
        r = await client.get(
            "/profiles/users",
            headers={"Authorization": f"Bearer {self.__class__.user_token}"}
        )
        assert r.status_code == 403

    async def test_15_coach_login_succes(self, client):
        r = await client.post(
            "/profiles/login",
            json={"email": "coach@example.com", "password": "CoachPass123!"}
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        self.__class__.coach_token = data["access_token"]
        assert "access_token" in r.json()

    async def test_15_coach_can_get_all_users(self, client):
        r = await client.get(
            "/profiles/users",
            headers={"Authorization": f"Bearer {self.__class__.coach_token}"}
        )
        assert r.status_code == 200

    async def test_16_admin_can_get_all_users(self, client):
        r = await client.get(
            "/profiles/users",
            headers={"Authorization": f"Bearer {self.__class__.admin_token}"}
        )
        assert r.status_code == 200

    async def test_17_admin_login_wrong_password(self, client):
        r = await client.post(
            "/profiles/login",
            json={"email": "admin@mail.fr", "password": "wrongpass"}
        )
        assert r.status_code == 401

    async def test_18_user_login_success(self, client):
        r = await client.post(
            "/profiles/login",
            json={"email": "alice@example.com", "password": "Secret123!"}
        )
        assert r.status_code == 200
        assert "access_token" in r.json()

    async def test_19_coach_cannot_delete_user(self, client):
        r = await client.delete(
            f"/profiles/{self.__class__.user_uuid}",
            headers={"Authorization": f"Bearer {self.__class__.coach_token}"}
        )
        assert r.status_code == 403
    
    async def test_20_user_cannot_get_user_profile(self, client):
        r = await client.get(
            f"/profiles/{self.__class__.coach_uuid}",
            headers={"Authorization": f"Bearer {self.__class__.user_token}"}
        )
        assert r.status_code == 403

    async def test_21_coach_can_get_user_profile(self, client):
        r = await client.get(
            f"/profiles/{self.__class__.user_uuid}",
            headers={"Authorization": f"Bearer {self.__class__.coach_token}"}
        )
        assert r.status_code == 200
        assert r.json()["id"] == self.__class__.user_uuid

    async def test_22_admin_can_get_user_profile(self, client):
        r = await client.get(
            f"/profiles/{self.__class__.coach_uuid}",
            headers={"Authorization": f"Bearer {self.__class__.admin_token}"}
        )
        assert r.status_code == 200
        assert r.json()["id"] == self.__class__.coach_uuid

    async def test_23_admin_get_user_profile_not_found(self, client):
        fake_id = str(uuid.uuid4())
        r = await client.get(
            f"/profiles/{fake_id}",
            headers={"Authorization": f"Bearer {self.__class__.admin_token}"}
        )
        assert r.status_code == 404

    async def test_24_user_can_delete_own_profile(self, client):
        r = await client.delete(
            f"/profiles/{self.__class__.user_uuid}",
            headers={"Authorization": f"Bearer {self.__class__.user_token}"}
        )
        assert r.status_code == 204

    async def test_25_admin_can_delete_coach(self, client):
        r = await client.delete(
            f"/profiles/{self.__class__.coach_uuid}",
            headers={"Authorization": f"Bearer {self.__class__.admin_token}"}
        )
        assert r.status_code == 204
