# ===== Workmate Dev Makefile =====
# Nutzung:
#   make help
#   make up / down / restart / ps / logs
#   make be / fe / db / db-clean
#   make migrate / makemigration MIG_MSG="add email"
#   make seed
#   make alembic-current / alembic-history
#   make be-sh / fe-sh / psql
#   make test
#   make fmt

SHELL := /bin/sh

# ---- Konfig ----
COMPOSE ?= docker compose
BACKEND_SVC ?= backend
FRONTEND_SVC ?= frontend
DB_SVC ?= db

# Seed-Datei (relativ zu /app im Backend-Container)
SEED_FILE ?= kit-staff/workmate_employees_basic.json

# Paketmanager-Helfer für Frontend (nur falls du das mal brauchst)
# Standard: npm. Für pnpm: PNPM=1 make <target>
ifeq ($(PNPM),1)
  PKG_CMD = sh -lc "corepack enable && pnpm i && pnpm dev --host 0.0.0.0 --port 5173"
else
  PKG_CMD = sh -lc "npm ci && npm run dev -- --host 0.0.0.0 --port 5173"
endif

.PHONY: help
help: ## Zeigt diese Hilfe
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | sed 's/:.*##/: /' | sort

# ---- Stack ----
.PHONY: up
up: ## Startet alle Services im Hintergrund
	$(COMPOSE) up -d

.PHONY: down
down: ## Stoppt alle Services (Daten bleiben erhalten)
	$(COMPOSE) down

.PHONY: restart
restart: ## Neustart aller Services
	$(COMPOSE) down
	$(COMPOSE) up -d

.PHONY: ps
ps: ## Zeigt Service-Status
	$(COMPOSE) ps

.PHONY: logs
logs: ## Folgt den Backend-Logs
	$(COMPOSE) logs -f $(BACKEND_SVC)

# ---- Teil-Starts ----
.PHONY: db
db: ## Startet nur DB + Adminer
	$(COMPOSE) up -d db adminer

.PHONY: be
be: ## Startet das Backend im Vordergrund (gut zum Debuggen)
	$(COMPOSE) up $(BACKEND_SVC)

.PHONY: fe
fe: ## Startet das Frontend im Vordergrund
	$(COMPOSE) up $(FRONTEND_SVC)

.PHONY: db-clean
db-clean: ## ⚠️ Stoppt Stack & löscht Volumes (frische DB!)
	$(COMPOSE) down -v

# ---- Alembic/Migrationen ----
.PHONY: migrate
migrate: ## Führt alembic upgrade head im Backend aus
	$(COMPOSE) exec $(BACKEND_SVC) alembic upgrade head

.PHONY: makemigration
makemigration: ## Erzeugt autogenerierte Migration (MIG_MSG='message' überschreibbar)
	@test -n "$(MIG_MSG)" || (echo "Bitte MIG_MSG=\"<beschreibung>\" setzen"; exit 1)
	$(COMPOSE) exec $(BACKEND_SVC) alembic revision --autogenerate -m "$(MIG_MSG)"

.PHONY: alembic-current
alembic-current: ## Zeigt aktuelle DB-Revision
	$(COMPOSE) exec $(BACKEND_SVC) alembic current

.PHONY: alembic-history
alembic-history: ## Zeigt Migrations-Historie
	$(COMPOSE) exec $(BACKEND_SVC) alembic history --verbose

# ---- Seeds & DB Tools ----
.PHONY: seed
seed: ## Lädt Seed-Daten in die DB (SEED_FILE variabel)
	$(COMPOSE) exec $(BACKEND_SVC) python kit-staff/seed_kit_team.py --file $(SEED_FILE)

.PHONY: psql
psql: ## Öffnet psql im DB-Container (nutzt POSTGRES_* aus .env)
	$(COMPOSE) exec $(DB_SVC) psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"

# ---- Shells ----
.PHONY: be-sh
be-sh: ## Shell im Backend-Container
	$(COMPOSE) exec $(BACKEND_SVC) sh

.PHONY: fe-sh
fe-sh: ## Shell im Frontend-Container
	$(COMPOSE) exec $(FRONTEND_SVC) sh

# ---- Tests & Format ----
.PHONY: test
test: ## Führt pytest im Backend aus (falls installiert)
	$(COMPOSE) exec $(BACKEND_SVC) pytest -q || true

.PHONY: fmt
fmt: ## Führt Formatter (black/isort/ruff) aus, wenn vorhanden
	$(COMPOSE) exec $(BACKEND_SVC) sh -lc "black app || true; isort app || true; ruff check app --fix || true"

.PHONY: ci
ci: ## Lokale CI-Nachbildung (DB->migrate->pytest)
	docker compose up -d db
	sleep 3
	docker compose exec backend alembic upgrade head
	docker compose exec backend pytest -q || true

.PHONY: build-be
build-be: ## Backend Dev-Image bauen
	docker build -f backend/Dockerfile.dev -t workmate/backend:dev .
