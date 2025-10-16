# app/tests/test_hr_access_and_export.py
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def make_test_user(role: str, email: str = ""):
    """Hilfsfunktion für simulierte User"""
    return json.dumps({
        "email": email or f"{role}@kit-it-koblenz.de",
        "role": role,
        "department": role,
        "preferred_username": role.capitalize(),
        "employee_id": f"KIT-{role.upper()}",
    })


# ✅ Zugriff erlaubt für Management
def test_hr_export_allowed_for_management():
    headers = {"X-Test-User": make_test_user("management")}
    res = client.get("/hr/reports/export?format=csv", headers=headers)
    print("Response Status:", res.status_code)
    print("Response Preview:", res.text[:200])
    assert res.status_code == 200
    assert "Employee ID" in res.text


# ✅ Zugriff erlaubt für HR
def test_hr_export_allowed_for_hr():
    headers = {"X-Test-User": make_test_user("hr")}
    res = client.get("/hr/reports/export?format=json", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "employees" in data
    assert "audits" in data


# ❌ Zugriff verweigert für Facility
def test_hr_overview_denied_for_facility():
    headers = {"X-Test-User": make_test_user("facility")}
    res = client.get("/hr/overview", headers=headers)
    assert res.status_code == 403


# ❌ Zugriff verweigert für Support
def test_hr_overview_denied_for_support():
    headers = {"X-Test-User": make_test_user("support")}
    res = client.get("/hr/overview", headers=headers)
    assert res.status_code == 403
