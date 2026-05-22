import pytest

@pytest.mark.asyncio
async def test_register_login_me(client):
    # Регистрация
    resp = await client.post("/auth/register", json={"email": "test@example.com", "password": "12345678"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"

    # Повторная регистрация - 409
    resp2 = await client.post("/auth/register", json={"email": "test@example.com", "password": "12345678"})
    assert resp2.status_code == 409

    # Логин
    resp3 = await client.post("/auth/login", data={"username": "test@example.com", "password": "12345678"})
    assert resp3.status_code == 200
    token = resp3.json()["access_token"]

    # /me с токеном
    resp4 = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp4.status_code == 200
    assert resp4.json()["email"] == "test@example.com"

    # /me без токена
    resp5 = await client.get("/auth/me")
    assert resp5.status_code == 401