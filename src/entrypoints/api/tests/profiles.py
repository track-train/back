import pytest
from uuid import uuid4
from container import container

@pytest.mark.asyncio
class TestProfiles:
    admin_token = ""
    user_token = ""
    user_uuid = ""

    async def test_create_profile_success(self, client):
        global user_token  
        global user_uuid

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

        user_token = body["token"]["access_token"]
        user_uuid = body["profile"]["id"]

        assert "profile" in body and "token" in body
        assert body["profile"]["email"] == "alice@example.com"

    async def test_create_duplicate_email_returns_400(self, client):
        payload = {
            "email": "bob@example.com",
            "password": "Pwd123!",
            "confirm_password": "Pwd123!",
            "name": "Bob"
        }

        r1 = await client.post("/profiles", json=payload)
        assert r1.status_code == 201

        r2 = await client.post("/profiles", json=payload)
        assert r2.status_code == 400
        assert "already exists" in r2.json()["detail"].lower()

    async def test_admin_login(self, client):
        global admin_token  

        admin_email = "admin@mail.fr"
        admin_password = "123456789"

        r = await client.post(
            "/profiles/login",
            json={"email": admin_email, "password": admin_password}
        )

        assert r.status_code == 200
        login_data = r.json()
        assert "access_token" in login_data, f"Access token is missing. Response: {login_data}"

        admin_token = login_data["access_token"]

    async def test_login_and_get_me(self, client):
        data = {
            "email": "charlie@example.com",
            "password": "TopSecret!",
            "confirm_password": "TopSecret!",
            "name": "Charlie"
        }

        r = await client.post("/profiles", json=data)
        token = r.json()["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        r2 = await client.get("/profiles/me", headers=headers)
        assert r2.status_code == 200
        assert r2.json()["email"] == "charlie@example.com"

    async def test_get_all_users_success(self, client):
        global admin_token  

        r = await client.get("/profiles/users", headers={"Authorization": f"Bearer {admin_token}"})

        assert r.status_code == 200
        users = r.json()
        assert isinstance(users, list)  

    async def test_get_all_users_forbidden_for_non_admin(self, client):
        global user_token  

        r = await client.get("/profiles/users", headers={"Authorization": f"Bearer {user_token}"})

        assert r.status_code == 403
        assert "access forbidden" in r.json()["detail"].lower()

    async def test_delete_profile_forbidden_for_non_owner_or_admin(self, client):
        global user_token  

        r = await client.delete("/profiles/874c4345-d070-49a0-9275-e4a2189d1f45", headers={"Authorization": f"Bearer {user_token}"})

        assert r.status_code == 403
        assert "access forbidden" in r.json()["detail"].lower()

    async def test_login_success(self, client):
        login_data = {
            "email": "alice@example.com",
            "password": "Secret123!"
        }

        r = await client.post("/profiles/login", json=login_data)

        assert r.status_code == 200
        assert "access_token" in r.json()  

    async def test_login_failed_wrong_password(self, client):
        login_data = {
            "email": "alice@example.com",
            "password": "WrongPassword"
        }

        r = await client.post("/profiles/login", json=login_data)

        assert r.status_code == 401
        assert "Invalid password or email" in r.json()["detail"]

    async def test_patch_profile_success(self, client):
        global user_token  
        global user_uuid

        update_data = {
            "name": "Updated User"
        }

        r = await client.patch(f"/profiles/{user_uuid}", json=update_data, headers={"Authorization": f"Bearer {user_token}"})

        assert r.status_code == 200
        assert r.json()["name"] == "Updated User"

    async def test_patch_profile_forbidden(self, client):
        global user_token  

        update_data = {"name": "Updated Name"}
        r = await client.patch("/profiles/874c4345-d070-49a0-9275-e4a2189d1f45", json=update_data, headers={"Authorization": f"Bearer {user_token}"})

        assert r.status_code == 403
        assert "Access forbidden" in r.json()["detail"]
    
    async def test_delete_profile_success_as_owner(self, client):
        global user_token  
        global user_uuid

        r = await client.delete(f"/profiles/{user_uuid}", headers={"Authorization": f"Bearer {user_token}"})

        assert r.status_code == 204
