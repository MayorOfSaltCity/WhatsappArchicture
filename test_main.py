from httpx import AsyncClient
import pytest
from main import app

@pytest.mark.anyio
async def test_create_announcement():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/announcements/", json={"message": "Test announcement"})
    assert response.status_code == 200
    result = response.json()
    assert result["announcement"]["message"] == "Test announcement"

@pytest.mark.anyio
async def test_get_announcement():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        post_response = await ac.post("/announcements/", json={"message": "Test announcement"})
        idempotency_key = post_response.json()["idempotency_key"]
        get_response = await ac.get(f"/announcements/{idempotency_key}")
    assert get_response.status_code == 200
    result = get_response.json()
    assert result["announcement"]["message"] == "Test announcement"
