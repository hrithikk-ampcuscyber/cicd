import httpx
import pytest


@pytest.mark.e2e
def test_health(base_url: str) -> None:
    response = httpx.get(f"{base_url}/health", timeout=10.0)
    response.raise_for_status()
    data = response.json()
    assert data["status"] == "ok"
    assert data["environment"] in {"test", "demo", "prod", "local"}


@pytest.mark.e2e
def test_create_item_flow(base_url: str) -> None:
    response = httpx.post(
        f"{base_url}/api/v1/items",
        json={"name": "E2E Item", "description": "created during e2e"},
        timeout=10.0,
    )
    response.raise_for_status()
    item = response.json()
    assert item["name"] == "E2E Item"

    get_response = httpx.get(f"{base_url}/api/v1/items/{item['id']}", timeout=10.0)
    get_response.raise_for_status()
    assert get_response.json()["name"] == "E2E Item"
