# seed_workmate.py
import argparse
import random
import string
from datetime import datetime, timedelta, timezone, date
from typing import Iterable, List
import requests

# ---------------------------
# CLI
# ---------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Seed or reset dummy data in Workmate API")
    p.add_argument("--base-url", default="http://localhost:8000", help="API base URL (no trailing slash)")
    p.add_argument("--employees", type=int, default=5, help="How many employees to create")
    p.add_argument("--reset", nargs="?", const="ALL",
                   help="Delete data. Options: ALL or comma list (employees,documents,reminders,sick-leaves,vacation-requests,time-entries)")
    return p.parse_args()

# ---------------------------
# Helpers
# ---------------------------
def iso_dt(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")

def rand_str(prefix: str, n: int = 6) -> str:
    import string as s
    return f"{prefix}-{''.join(random.choices(s.ascii_lowercase + s.digits, k=n))}"

def pick(seq):
    return random.choice(seq)

def get(session: requests.Session, url: str):
    r = session.get(url, timeout=30)
    if not r.ok:
        raise RuntimeError(f"GET {url} failed [{r.status_code}]: {r.text}")
    return r.json()

def post(session: requests.Session, url: str, payload: dict):
    r = session.post(url, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"POST {url} failed [{r.status_code}]: {r.text}")
    return r.json()

def put(session: requests.Session, url: str, payload: dict):
    r = session.put(url, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"PUT {url} failed [{r.status_code}]: {r.text}")
    return r.json()

def delete(session: requests.Session, url: str) -> None:
    r = session.delete(url, timeout=30)
    if r.status_code not in (200, 202, 204):
        raise RuntimeError(f"DELETE {url} failed [{r.status_code}]: {r.text}")

def ensure_trailing_slash(base: str) -> str:
    return base.rstrip("/")

# ---------------------------
# Endpoints (adjust here if you use a prefix)
# ---------------------------
def ep(base: str, name: str) -> str:
    # Returns collection endpoint (with trailing slash)
    return f"{base}/{name.strip('/')}/"

COLLECTIONS = {
    "employees": "employees",
    "documents": "documents",
    "reminders": "reminders",
    "sick-leaves": "sick-leaves",
    "vacation-requests": "vacation-requests",
    "time-entries": "time-entries",
}

# ---------------------------
# Seeders
# ---------------------------
DOC_TYPES = ["attest", "urlaubsantrag", "bewerbung", "krankenkasse", "fehlzeit", "sonstige"]
DOC_STATUS = ["pending", "received", "processed"]
REM_STATUS = ["pending", "done"]
VAC_STATUS = ["pending", "approved", "rejected"]

DEPTS = ["Vertrieb", "Support", "Entwicklung", "HR", "Ops"]
POS   = ["Junior", "Senior", "Lead", "Werkstudent:in", "Manager:in"]

def seed_employee(session: requests.Session, base: str) -> dict:
    name = f"{pick(['Lena','Max','Sara','Jonas','Mira','Timo','Noah','Lea','Ben','Emma'])} {pick(['Müller','Kraus','Vogel','Schmidt','Nguyen','Klein','Weber','Hoffmann'])}"
    emp_id = rand_str("EMP", 5).upper()
    payload = {
        "name": name,
        "email": f"{emp_id.lower()}@example.com",
        "employee_id": emp_id,  # string business id
        "department": pick(DEPTS),
        "position": pick(POS),
        "start_date": str(date.today() - timedelta(days=random.randint(10, 400))),
        "vacation_days_total": 30,
        "vacation_days_used": random.randint(0, 5),
    }
    return post(session, ep(base, "employees"), payload)

def seed_document(session: requests.Session, base: str, emp: dict) -> dict:
    dt_now = datetime.now(timezone.utc)
    payload = {
        "employee_id": emp["id"],
        "document_type": pick(DOC_TYPES),
        "title": f"Dokument {rand_str('Ref', 4)}",
        "file_url": f"https://files.example.com/{rand_str('doc',8)}.pdf",
        "is_original_required": random.choice([True, False]),
        "status": pick(DOC_STATUS),
        "upload_date": iso_dt(dt_now - timedelta(days=random.randint(0, 10), hours=random.randint(0, 8))),
        "notes": random.choice([None, "Bitte Original nachreichen", "Per E-Mail erhalten", "Gelesen"]),
    }
    return post(session, ep(base, "documents"), payload)

def seed_reminder(session: requests.Session, base: str, emp: dict) -> dict:
    dt_now = datetime.now(timezone.utc)
    due = dt_now + timedelta(hours=random.randint(-72, 120))
    payload = {
        "employee_id": emp["id"],
        "title": pick(["Attest nachreichen", "Urlaub prüfen", "KK-Nachweis prüfen", "Unterlagen versenden"]),
        "description": random.choice([None, "Bitte bis 16:00 erledigen", "Dringend", ""]),
        "due_at": iso_dt(due),
    }
    return post(session, ep(base, "reminders"), payload)

def seed_sick_leave(session: requests.Session, base: str, emp: dict, maybe_doc: dict | None) -> dict:
    dt_now = datetime.now(timezone.utc)
    start = dt_now - timedelta(days=random.randint(0, 7))
    end   = start + timedelta(days=random.randint(1, 4))
    payload = {
        "employee_id": emp["id"],
        "start_date": iso_dt(start.replace(hour=7, minute=0)),
        "end_date":   iso_dt(end.replace(hour=18, minute=0)),
        "document_id": (maybe_doc["id"] if maybe_doc and random.random() < 0.6 else None),
        "notes": random.choice([None, "Grippaler Infekt", "Rücken", "Migräne"]),
    }
    return post(session, ep(base, "sick-leaves"), payload)

def seed_vacation(session: requests.Session, base: str, emp: dict) -> dict:
    start = date.today() + timedelta(days=random.randint(20, 120))
    end   = start + timedelta(days=random.randint(3, 12))
    payload = {
        "employee_id": emp["id"],
        "start_date": str(start),
        "end_date":   str(end),
        "reason": random.choice([None, "Familienreise", "Städtetrip", "Erholung"]),
        "status": pick(VAC_STATUS),
        "representative": random.choice([None, "Max Muster", "Lea Beispiel"]),
        "notes": random.choice([None, "Hotel gebucht", "Flexible Termine"]),
    }
    vr = post(session, ep(base, "vacation-requests"), payload)

    # Beispiel-Update via PUT (halbwegs realistisch)
    if vr["status"] == "pending" and random.random() < 0.5:
        vr = put(session, f"{ep(base, 'vacation-requests')}{vr['id']}", {"status": "approved", "notes": "Automatisch genehmigt"})
    return vr

def seed_time_entries(session: requests.Session, base: str, emp: dict) -> List[dict]:
    entries = []
    for _ in range(random.randint(1, 3)):
        start = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 5), hours=random.randint(3, 8))
        end   = start + timedelta(hours=random.randint(4, 9), minutes=random.randint(0, 45))
        payload = {
            "employee_id": emp["id"],
            "start_time": iso_dt(start),
            "end_time": iso_dt(end),
            "notes": random.choice([None, "Kundentermin", "Remote-Work", "Doku geschrieben"]),
        }
        entries.append(post(session, ep(base, "time-entries"), payload))
    return entries

# ---------------------------
# Reset helpers
# ---------------------------
# In welcher Reihenfolge löschen?
# - Wenn Employees gelöscht werden, räumt CASCADE fast alles weg.
# - Für selektiven Reset: erst abhängige Entitäten, dann Employees.
DELETE_ORDER = [
    "time-entries",
    "reminders",
    "sick-leaves",
    "documents",
    "vacation-requests",
    "employees",
]

def list_ids(session: requests.Session, base: str, collection: str) -> list[str]:
    items = get(session, ep(base, collection))
    if not isinstance(items, list):
        # Falls dein List-Endpoint paginiert (items in 'data' o.ä.)
        items = items.get("items") or items.get("data") or []
    return [it["id"] for it in items]

def reset_collections(session: requests.Session, base: str, targets: Iterable[str]):
    # Normalisieren & validieren
    targets = [t.strip() for t in targets if t.strip()]
    for t in targets:
        if t not in COLLECTIONS:
            raise SystemExit(f"Unknown collection '{t}'. Allowed: {', '.join(COLLECTIONS)}")

    # Reihenfolge respektieren
    ordered = [c for c in DELETE_ORDER if c in targets]

    for coll in ordered:
        try:
            ids = list_ids(session, base, coll)
        except Exception as e:
            print(f"[WARN] List {coll} failed: {e}")
            continue

        if not ids:
            print(f"[{coll}] nothing to delete")
            continue

        print(f"[{coll}] deleting {len(ids)} items ...")
        for _id in ids:
            try:
                delete(session, f"{ep(base, coll)}{_id}")
            except Exception as e:
                print(f"  - delete {coll}/{_id} failed: {e}")
        print(f"[{coll}] done.")

# ---------------------------
# Main
# ---------------------------
def main():
    args = parse_args()
    base = ensure_trailing_slash(args.base_url)

    s = requests.Session()

    # RESET?
    if args.reset:
        if args.reset == "ALL":
            targets = list(COLLECTIONS.keys())
        else:
            targets = args.reset.split(",")
        print(f"Resetting: {', '.join(targets)}")
        reset_collections(s, base, targets)
        print("Reset complete.")
        return

    # SEED
    print(f"Seeding against {base} ...")
    employees = []
    for _ in range(args.employees):
        emp = seed_employee(s, base)
        employees.append(emp)
        print(f"[EMP] {emp['id']}  {emp['name']}  {emp['email']}")

        docs = []
        for _ in range(random.randint(1, 2)):
            d = seed_document(s, base, emp)
            docs.append(d)
            print(f"  [DOC] {d['id']}  {d['title']}  ({d['status']})")

        for _ in range(random.randint(1, 2)):
            r = seed_reminder(s, base, emp)
            print(f"  [REM] {r['id']}  due_at={r.get('due_at')}")

        if random.random() < 0.7:
            sl = seed_sick_leave(s, base, emp, docs[0] if docs else None)
            print(f"  [SL ] {sl['id']}  {sl['start_date']} → {sl['end_date']}")

        if random.random() < 0.8:
            vr = seed_vacation(s, base, emp)
            print(f"  [VAC] {vr['id']}  {vr['status']}  {vr['start_date']}..{vr['end_date']}")

        tes = seed_time_entries(s, base, emp)
        for te in tes:
            print(f"  [TE ] {te['id']}  {te['start_time']} → {te.get('end_time')}")

    print(f"Done. Seeded {len(employees)} employees with related records.")

if __name__ == "__main__":
    main()
