from tests.conftest import auth_headers, login


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_success(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"
    assert "asset:read" in data["user"]["permissions"]


def test_login_wrong_password(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_me_requires_auth(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_token(client):
    token = login(client, "admin", "admin123")
    response = client.get("/api/auth/me", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert "系统管理员" in response.json()["roles"]
