from fastapi.testclient import TestClient

from app.main import app
from app.routers import items


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "environment" in payload
    assert "version" in payload


def test_list_items_empty() -> None:
    items.clear_items()
    client = TestClient(app)
    response = client.get("/api/v1/items")
    assert response.status_code == 200
    assert response.json() == []
