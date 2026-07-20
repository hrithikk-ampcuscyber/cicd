from fastapi.testclient import TestClient

from app.main import app
from app.routers import items


def test_create_and_get_item() -> None:
    items.clear_items()
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/items",
        json={"name": "Widget", "description": "A test widget"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Widget"
    assert created["id"] == 1

    get_response = client.get("/api/v1/items/1")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Widget"


def test_get_missing_item_returns_404() -> None:
    items.clear_items()
    client = TestClient(app)

    response = client.get("/api/v1/items/999")
    assert response.status_code == 404
