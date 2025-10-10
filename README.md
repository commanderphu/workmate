[![CI Status](https://github.com/commanderphu/workmate/actions/workflows/ci.yml)

# 🧠 Workmate – The Digital Backoffice by K.I.T. Solutions 

> *„Automatisiere das, was dich aufhält. Lebe das, was dich antreibt.“*  

---

## 📖 Über Workmate

**Workmate** ist das interne **HR-, Verwaltungs- und Automatisierungssystem**  
von [K.I.T. Solutions](https://kit-it-koblenz.de).  
Es wurde entwickelt, um **Verwaltung, Backoffice und interne Workflows**  
in einer klaren, ethischen und offenen IT-Umgebung zu bündeln.  

Ziel ist es, ein **modulares, lokal hostbares System** zu schaffen, das  
ohne externe Cloud-Dienste funktioniert – ganz im Sinne des K.I.T.-Leitsatzes:  
> 🧩 *„IT muss nicht schmutzig sein.“*

---

## 🏗️ Aktueller Stand (Oktober 2025)

- Entwicklungsstatus: **Pre-Alpha / lokal aktiv in Entwicklung**
- Architektur: **FastAPI (Backend)** + **PostgreSQL** + **Vue/React (Frontend)**
- Status: Läuft lokal auf PC/Notebook, Backend & Frontend manuell gestartet
- Geplant: Docker-Compose Setup & Deployment auf K.I.T.-Servern

---

## ⚙️ Tech Stack

| Komponente | Technologie | Beschreibung |
|-------------|--------------|---------------|
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) | API, Authentifizierung, Logik |
| **Datenbank** | PostgreSQL | zentrale Datenhaltung |
| **Frontend** | Vue 3 / React | Benutzeroberfläche (noch im Aufbau) |
| **ORM** | SQLAlchemy | Datenbankanbindung |
| **Containerisierung (geplant)** | Docker / Compose | lokale & produktive Deployments |
| **Reverse Proxy (später)** | Traefik | interne Diensteverwaltung |
| **Integration (später)** | Paperless NGX, Nextcloud | Dokumente, HR-Unterlagen, Sync |

---

## 📂 Projektstruktur (aktuell)

```yaml
workmate/
├── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── models/
│ │ ├── routers/
│ │ └── core/
│ ├── requirements.txt
│ └── .env
│
├── frontend/
│ ├── src/
│ ├── public/
│ └── package.json
│
├── docker-compose.yml (in Planung)
└── README.md
```


---

## 🚀 Lokale Entwicklung

### 1️⃣ Backend starten

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Entwicklungsserver starten
uvicorn app.main:app --reload
```

Server läuft dann standardmäßig unter:
➡️ [API/Backend](http://127.0.0.1:8000/docs)

### 2️⃣ Frontend starten

```bash
Code kopieren
cd frontend
pnpm install
pnpm run dev
```

Frontend läuft unter:
➡️ [Frontend](http://127.0.0.1:5173)

### 3️⃣ Datenbank (PostgreSQL)

Aktuell lokal oder via Docker-Container (optional):

```bash
Code kopieren
docker run --name workmate-db -e POSTGRES_USER=einfachnurphu \
  -e POSTGRES_PASSWORD=deinpasswort \
  -e POSTGRES_DB=workmate \
  -p 5432:5432 -d postgres
```  
---

## 🧩 Aktuelle Module

Modul | Beschreibung | Status
|-----|-----|------|
Dashboard | Übersicht über Reminder, Mitarbeiter, Dokumente | 🟢 in Entwicklung
HR / Employee | Mitarbeiterdaten, Verträge, Rollen | 🟡 Basisstruktur vorhanden
Reminder | Aufgaben, Fristen, Erinnerungen | 🟢 funktionsfähig
Vacation / Absences | Urlaubsplanung & Abwesenheiten | 🟡 Konzept vorhanden
Documents (Paperless) | Verknüpfung mit Paperless NGX | 🔜 geplant
Auth / Login | Nutzerverwaltung, Sessions | 🔜 geplant
Finance / Projects | Rechnungen, Projekte, Zeitaufwand |🔜 geplant

---

## 🧠 Vision (Phase 2–3)

Vollständige Automatisierung durch **Gideon** (Monitoring, KI, Workflows)

Integration mit **Paperless NGX** (Dokumentenarchivierung)

Integration mit **Nextcloud** (Dateiverwaltung)

Erweiterte Module:

✅ HR & Onboarding

✅ Reminder & Aufgaben

✅ Support / Tickets

✅ Finanzen & Buchhaltung

✅ Zeiterfassung

Ziel ist eins **sauberes, modulares Intranet-System** für kleine Unternehmen,
Freelancer & nachhaltige IT-Teams.

---

## 🧰 Entwicklungs-Notizen

Entwickelt von: **Joshua Phu Bein (K.I.T. Solutions)**

Aktuelle Version: `v0.1-dev`

Entwicklungsphase: Backend + UI-Integration

Repository: [GitHub (privat / dev)](https://github.com/commanderphu/workmate)

Betriebssystem: Fedora Linux

Lokales Testsystem: Unraid + Docker (Paperless / Wiki.js etc.)

---

## 🧾 Lizenz

© 2025 K.I.T. Solutions – Alle Rechte vorbehalten.
Dieses Projekt ist Teil der internen Toolchain von K.I.T. Solutions (Koblenz).
Eine Open-Source-Version ist langfristig geplant.

---

## 💬 Kontakt

K.I.T. Solutions
Joshua Phu Bein
📍 Koblenz, Deutschland
🌐 [kit-it-koblenz.de](https://kit-it-koblenz.de)
📧 [info[at]kit-it-koblenz.de](mailto://info@kit-it-koblenz.de)

---
