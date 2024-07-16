from fastapi.testclient import TestClient


def test_get_user_list(client: TestClient, apply_migrations: None):
    response = client.get('/users/')
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert type(data["users"]) is list
