from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)

def test_live_ok():
    r = c.get("/api/live")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ok"
    assert "details" in j and "time" in j["details"]

def test_health_shape():
    r = c.get("/api/health")
    assert r.status_code == 200
    j = r.json()
    assert "status" in j and "details" in j

# Optional: ready kann je nach Testumgebung 200 oder 503 liefern
def test_ready_http_code_is_valid():
    r = c.get("/api/ready")
    assert r.status_code in (200, 503)
