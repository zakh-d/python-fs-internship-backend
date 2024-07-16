from fastapi.testclient import TestClient
import pytest


@pytest.mark.asyncio
async def test_complete_health_check(client: TestClient, apply_migrations: None):
    response = client.get('/health')
    assert response.status_code == 200

    data = response.json()

    assert 'app' in data
    assert 'redis' in data
    assert 'db' in data

    assert data['app']['status_code'] == 200
