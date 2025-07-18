# src/entrypoints/api/tests/test_profiles.py
import pytest
from uuid import uuid4

@pytest.mark.asyncio
class TestProfiles:

    async def test_create_profile_success(self, client):
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
        assert "duplicate" in r2.json()["detail"].lower()

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

    async def test_login_bad_credentials_returns_401(self, client, seed_data):
        admin, _ = seed_data["admin"]
        r = await client.post(
            "/profiles/login",
            json={"email": admin.email, "password": "wrong!"}
        )
        assert r.status_code == 401

    async def test_get_all_users_requires_admin_and_returns_list(self, client, seed_data):
        # sans token → 403
        r1 = await client.get("/profiles/users")
        assert r1.status_code == 403

        # avec token admin
        admin, admin_pw = seed_data["admin"]
        r_login = await client.post(
            "/profiles/login",
            json={"email": admin.email, "password": admin_pw}
        )
        token = r_login.json()["access_token"]
        r2 = await client.get(
            "/profiles/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert r2.status_code == 200
        users = r2.json()
        assert any(u["email"] == admin.email for u in users)

    async def test_get_coach_profiles_empty_and_after_creation(self, client):
        # d'abord, aucun coach
        r1 = await client.get("/profiles/coachs")
        assert r1.status_code == 200
        assert r1.json() == []

        # on en crée un
        payload = {
            "email": "coach2@example.com",
            "password": "Coach123!",
            "confirm_password": "Coach123!",
            "name": "Coach2"
        }
        r2 = await client.post("/profiles", json=payload)
        assert r2.status_code == 201

        # puis on vérifie
        r3 = await client.get("/profiles/coachs")
        emails = [c["email"] for c in r3.json()]
        assert "coach2@example.com" in emails

    async def test_delete_profile_owner_or_admin(self, client, seed_data):
        # crée Dave
        r = await client.post(
            "/profiles",
            json={"email": "dave@example.com", "password": "Pwd!", "confirm_password": "Pwd!"}
        )
        pid = r.json()["profile"]["id"]
        token_owner = r.json()["token"]["access_token"]

        # crée Eve
        r_e = await client.post(
            "/profiles",
            json={"email": "eve@example.com", "password": "Pwd!", "confirm_password": "Pwd!"}
        )
        token_e = r_e.json()["token"]["access_token"]

        # forbidden pour Eve
        r_f = await client.delete(
            f"/profiles/{pid}", headers={"Authorization": f"Bearer {token_e}"}
        )
        assert r_f.status_code == 403

        # suppression par le propriétaire
        r_ok = await client.delete(
            f"/profiles/{pid}", headers={"Authorization": f"Bearer {token_owner}"}
        )
        assert r_ok.status_code == 204

        # tentative de suppressions ultérieure → 404
        r_nf = await client.delete(
            f"/profiles/{pid}", headers={"Authorization": f"Bearer {token_owner}"}
        )
        assert r_nf.status_code == 404

    async def test_patch_profile_and_404(self, client):
        fake_id = str(uuid4())
        r_nf = await client.patch(f"/profiles/{fake_id}", json={"name": "New"})
        assert r_nf.status_code in (403, 404)

        # création puis patch réussi
        r = await client.post(
            "/profiles",
            json={"email": "guy@example.com", "password": "Pwd!", "confirm_password": "Pwd!"}
        )
        pid = r.json()["profile"]["id"]
        token = r.json()["token"]["access_token"]

        r_patch = await client.patch(
            f"/profiles/{pid}",
            json={"name": "Guy Updated"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert r_patch.status_code == 200
        assert r_patch.json()["name"] == "Guy Updated"

    async def test_patch_email_duplicate_and_notfound(self, client):
        # on crée deux profils
        r1 = await client.post(
            "/profiles", json={"email": "foo@example.com", "password": "A1!", "confirm_password": "A1!"}
        )
        r2 = await client.post(
            "/profiles", json={"email": "bar@example.com", "password": "B2!", "confirm_password": "B2!"}
        )
        id1   = r1.json()["profile"]["id"]
        token = r2.json()["token"]["access_token"]

        # on tente un duplicate email
        r_dup = await client.patch(
            f"/profiles/{id1}/email",
            json={"email": "foo@example.com"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert r_dup.status_code == 400

        # on tente sur ID inexistant
        fake = str(uuid4())
        r_nf = await client.patch(
            f"/profiles/{fake}/email",
            json={"email": "x@y.com"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert r_nf.status_code == 404

    async def test_patch_password(self, client):
        # création
        r = await client.post(
            "/profiles",
            json={"email": "harry@example.com", "password": "OldPass!", "confirm_password": "OldPass!"}
        )
        pid   = r.json()["profile"]["id"]
        token = r.json()["token"]["access_token"]

        # mauvais ancien mot de passe
        r_bad = await client.patch(
            f"/profiles/{pid}/password",
            json={"old_password": "Bad!", "new_password": "NewPass!"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert r_bad.status_code == 400

        # correct
        r_ok = await client.patch(
            f"/profiles/{pid}/password",
            json={"old_password": "OldPass!", "new_password": "NewPass!"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert r_ok.status_code == 204

    async def test_patch_roles_protected_and_success(self, client, seed_data):
        # création d'un user lambda
        r = await client.post(
            "/profiles",
            json={"email": "ian@example.com", "password": "Pwd!", "confirm_password": "Pwd!"}
        )
        pid        = r.json()["profile"]["id"]
        token_user = r.json()["token"]["access_token"]

        # il ne peut pas se donner des rôles
        r_403 = await client.patch(
            f"/profiles/{pid}/roles",
            json={"roles": ["admin"]},
            headers={"Authorization": f"Bearer {token_user}"}
        )
        assert r_403.status_code == 403

        # l'admin peut
        admin, admin_pw = seed_data["admin"]
        r_login = await client.post(
            "/profiles/login",
            json={"email": admin.email, "password": admin_pw}
        )
        token_admin = r_login.json()["access_token"]

        r_admin = await client.patch(
            f"/profiles/{pid}/roles",
            json={"roles": ["coach"]},
            headers={"Authorization": f"Bearer {token_admin}"}
        )
        assert r_admin.status_code == 200
        assert "coach" in r_admin.json()["roles"]
