# seed_kit_team.py
import argparse
import json
import requests
from pathlib import Path

# ---------------------------
# Helpers
# ---------------------------
def ensure_trailing_slash(base: str) -> str:
    return base.rstrip("/")

def ep(base: str, name: str) -> str:
    return f"{base}/{name.strip('/')}/"

def post(session: requests.Session, url: str, payload: dict):
    r = session.post(url, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"POST {url} failed [{r.status_code}]: {r.text}")
    return r.json()

# ---------------------------
# Seeder
# ---------------------------
def seed_from_file(session: requests.Session, base: str, filepath: str):
    path = Path(filepath)
    if not path.exists():
        raise SystemExit(f"File {filepath} not found.")

    with path.open("r", encoding="utf-8") as f:
        if filepath.endswith(".json"):
            employees = json.load(f)
        else:
            raise SystemExit("Only JSON supported for now.")

    print(f"Seeding {len(employees)} employees from {filepath} …")

    for emp in employees:
        payload = {
            "employee_id": emp["employee_id"],
            "name": f"{emp['first_name']} {emp['last_name']}",
            "email": emp["email"],
            "department": emp["department"],
            "position": emp["role_title"],
            "start_date": emp.get("start_date") or "2024-05-01",
            "vacation_days_total": 30,
            "vacation_days_used": 0,
        }
        created = post(session, ep(base, "employees"), payload)
        print(f"[EMP] {created['id']} {created['name']} {created['email']}")

    print("✅ Seeding complete.")

# ---------------------------
# Main
# ---------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Seed KIT Solutions team into Workmate API")
    p.add_argument("--base-url", default="http://localhost:8000", help="API base URL (no trailing slash)")
    p.add_argument("--file", required=True, help="Path to employees JSON file")
    return p.parse_args()

def main():
    args = parse_args()
    base = ensure_trailing_slash(args.base_url)
    s = requests.Session()
    seed_from_file(s, base, args.file)

if __name__ == "__main__":
    main()
