import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_healthz():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/healthz")
    assert res.status_code == 200
    assert res.json().get("status") == "ok"
