import os, uuid, requests
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")




def test_employees_roundtrip():
    u = uuid.uuid4().hex[:8]
    payload = {
    "name": f"Test User {u}",
    "email": f"test{u}@example.com",
    "employee_id": f"EMP{u}",
    "department": "QA",
    "position": "Tester",
    "start_date": "2025-08-01"
    }
    r = requests.post(f"{BASE_URL}/employees/", json=payload)
    assert r.status_code == 200
    emp = r.json()
    emp_id = emp["id"]
    r2 = requests.get(f"{BASE_URL}/employees/{emp_id}")
    assert r2.status_code == 200




def test_documents_roundtrip():
    emp_id = requests.get(f"{BASE_URL}/employees/").json()[0]["id"]
    doc_payload = {
    "employee_id": emp_id,
    "document_type": "attest",
    "title": "TestDoc",
    "file_url": "http://files/test.pdf",
    "is_original_required": False,
    "status": "pending",
    "notes": "SmokeTest"
    }
    r = requests.post(f"{BASE_URL}/documents/", json=doc_payload)
    assert r.status_code == 200
    doc = r.json()
    r2 = requests.get(f"{BASE_URL}/documents/{doc['id']}")
    assert r2.status_code == 200




def test_sick_leaves_roundtrip():
    emp_id = requests.get(f"{BASE_URL}/employees/").json()[0]["id"]
    sl_payload = {
    "employee_id": emp_id,
    "start_date": "2025-08-10",
    "end_date": "2025-08-12",
    "document_id": None,
    "notes": "TestSL"
    }
    r = requests.post(f"{BASE_URL}/sick-leaves/", json=sl_payload)
    assert r.status_code == 200
    sl = r.json()
    r2 = requests.get(f"{BASE_URL}/sick-leaves/{sl['id']}")
    assert r2.status_code == 200




def test_reminders_roundtrip():
    emp_id = requests.get(f"{BASE_URL}/employees/").json()[0]["id"]
    rem_payload = {
    "employee_id": emp_id,
    "title": "ReminderTest",
    "description": "TestDesc",
    "due_at": "2025-09-01T09:00:00Z",
    "status": "pending",
    "linkedTo": None
    }
    r = requests.post(f"{BASE_URL}/reminders/", json=rem_payload)
    assert r.status_code == 200
    rem = r.json()
    r2 = requests.get(f"{BASE_URL}/reminders/{rem['id']}")
    assert r2.status_code == 200