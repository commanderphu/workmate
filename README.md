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
