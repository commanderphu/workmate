# Workmate 🗂️

**Workmate** ist ein internes Tool zur Verwaltung von administrativen Workflows  
(Personalakte, Krankmeldungen, Urlaubsanträge, Zeiterfassung, Monatsabrechnung).  
Es soll den Büroalltag erleichtern und Prozesse digitalisieren.

---

## 🚀 Features
- 📁 **Personalakte** – Dokumentenverwaltung pro Mitarbeiter
- 🏥 **Krankmeldungen** – inkl. Upload von Attesten
- 🌴 **Urlaubsanträge** – Status & Genehmigungen
- ⏱️ **Zeiterfassung** – Übersicht, Verlinkungen (z. B. Timeboard, Fieldglass)
- 📅 **Reminders** – ToDo-System mit Fälligkeiten & Status
- 📊 **Dashboard** – zentrale Übersicht über wichtige Daten

## 🔍 Feature-Rundgang
Damit du dir schneller einen Eindruck verschaffen kannst, wie sich die API im Alltag verhält, findest du hier einen kurzen Walkthrough der wichtigsten Endpunkte.

### Mitarbeiterverwaltung
- `GET /employees/` listet Mitarbeitende mit Such- und Paging-Parametern, z. B. `q`, `limit` oder `offset`, um gezielt Personalakten zu finden.【F:backend/app/routers/employees.py†L17-L31】
- `POST /employees/` legt neue Mitarbeitende an und vergibt dabei automatisch eine UUID als Primärschlüssel sowie Zeitstempel für `created` und `updated`.【F:backend/app/routers/employees.py†L33-L48】
- Für Korrekturen gibt es `PUT /employees/{id}` bzw. `DELETE /employees/{id}`; alternativ kannst du mit `PUT /employees/by_business/{employee_id}` auch über die externe Personalnummer aktualisieren, inklusive Konfliktprüfung auf doppelte E-Mails.【F:backend/app/routers/employees.py†L50-L97】

### Dokumente & Krankmeldungen
- `POST /documents/` hinterlegt Dateien wie Atteste oder Verträge zu einem Mitarbeitenden und speichert Status, Upload-Datum und optionale Notizen.【F:backend/app/routers/documents.py†L12-L37】
- `GET /documents/` bietet Filter nach Mitarbeitenden, Status, Dokumenttyp und Freitextsuche in Titel/Notizen – ideal für Audits.【F:backend/app/routers/documents.py†L22-L37】
- Krankmeldungen werden über `POST /sick-leaves/` inkl. Verknüpfung zu einem Dokument erfasst; die Liste ist über optionale Filter wie `employee_id` und Pagination zugänglich.【F:backend/app/routers/sick_leaves.py†L14-L35】

### Urlaubsverwaltung & Zeiterfassung
- Urlaubsanträge kommen über `POST /vacation-requests/` ins System; sie tragen Statuswerte wie `pending`, `approved` oder `rejected`, die per Update-Endpunkt angepasst werden können.【F:backend/app/models.py†L108-L151】
- Die Zeiterfassung (`/time-entries/`) speichert Start-/Endzeiten inklusive Notizen und lässt sich für einzelne Mitarbeitende filtern, um Tages- oder Wochenübersichten zu erzeugen.【F:backend/app/routers/time_entries.py†L9-L37】

### Reminder & ToDo-Management
- `POST /reminders/` legt Aufgaben mit Fälligkeit an und berechnet serverseitig ein `is_overdue`-Flag, sobald eine offene Aufgabe überfällig ist.【F:backend/app/routers/reminders.py†L54-L96】
- Für Fachbereiche ohne UUID-Kenntnis gibt es Business-Routen wie `GET /reminders/by_business/{employee_id}`, die automatisch nach der Personalnummer auflösen und sortiert zurückgeben.【F:backend/app/routers/reminders.py†L26-L52】
- Statuswechsel (z. B. erledigt markieren) erfolgen bequem über `POST /reminders/{id}/done`.【F:backend/app/routers/reminders.py†L124-L143】

### Daten befüllen & Demo
- Mit `python backend/seed_workmate.py --employees 5` lässt sich eine lokale Instanz per REST-Calls mit Testdaten füllen. Das Skript erzeugt Mitarbeitende, Dokumente, Reminder, Krankmeldungen, Urlaube und Zeiteinträge in einem Rutsch.【F:backend/seed_workmate.py†L1-L132】

---

## 🛠️ Tech Stack
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)  
- **Database**: PostgreSQL  
- **ORM**: SQLAlchemy  
- **Migrations**: Alembic  
- **Frontend (geplant)**: SvelteKit / Vue / React  
- **Automatisierungen (optional)**: n8n  
- **Deployment**: Docker & Docker Compose, Unraid/Hetzner  

---

## 📂 Projektstruktur
```
workmate/
├── backend/
│   ├── app/
│   │   ├── main.py          # Einstiegspunkt
│   │   ├── models.py        # SQLAlchemy-Modelle
│   │   ├── schemas.py       # Pydantic-Schemas
│   │   ├── database.py      # DB-Setup
│   │   ├── routers/         # API-Router (Employees, SickLeaves, ...)
│   │   └── core/            # Konfiguration, Security, Utils
│   ├── alembic/             # Migrationen
│   └── tests/               # Unit- & Integrationstests
├── frontend/                # (noch in Entwicklung)
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## ⚙️ Installation & Setup

### Voraussetzungen
- Python **3.11+**  
- PostgreSQL  
- (Optional) Docker & Docker Compose  

### Schritte
```bash
# Repository klonen
git clone https://github.com/USERNAME/workmate.git
cd workmate

# Dependencies installieren
pip install -r requirements.txt

# .env anlegen
cp .env.example .env

# Datenbank migrieren
alembic upgrade head

# Starten
uvicorn app.main:app --reload
```

### Mit Docker starten
```bash
docker-compose up -d
```

API verfügbar unter:  
- Swagger UI → http://localhost:8000/docs  
- ReDoc → http://localhost:8000/redoc  

---

## 🧪 Tests
```bash
pytest
```

---

## 📌 Roadmap
- [x] Basis-API für Mitarbeiterverwaltung  
- [x] Krankmeldungen & Urlaubsanträge  
- [x] Reminder-/Fristensystem  
- [ ] Dashboard mit Analytics  
- [ ] Frontend-UI (SvelteKit/Vue/React)  
- [ ] Authentifizierung & Rollen  
- [ ] Cloud-Deployment (Hetzner / Unraid)  

---

## 🤝 Contribution
Pull Requests sind willkommen!  
Für größere Änderungen bitte zuerst ein **Issue** eröffnen, um die Änderungen zu besprechen.  

---

## 📜 Lizenz
MIT License © 2025 Joshua Phu Bein
