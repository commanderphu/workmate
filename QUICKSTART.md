# Workmate – Developer Quickstart ⚡

Dieses Dokument ist für interne Entwickler gedacht, die schnell loslegen wollen.

---

## 🚀 Setup
```bash
git clone https://github.com/USERNAME/workmate.git
cd workmate

cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

---

## 🗄️ Datenbank
- PostgreSQL nutzen
- Migrationen mit Alembic:
```bash
alembic revision --autogenerate -m "Message"
alembic upgrade head
```

---

## 🧪 Tests
```bash
pytest
```

---

## 🌐 API
- Swagger → http://localhost:8000/docs  
- ReDoc → http://localhost:8000/redoc  

---

## 🔑 Tipps
- `.env` immer aktuell halten (DB-URL, Secrets)  
- Seeds für Testdaten können unter `backend/tests/seeds/` eingespielt werden  
- Für Dev reicht `uvicorn`; Prod besser `gunicorn` + Docker  
