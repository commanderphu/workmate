# ===== Workmate Dev Makefile =====
# Usage:
#   make help
#   make up / down / restart / ps
#   make be-logs / fe-logs / be-restart / fe-restart
#   make rebuild-ui / rebuild-be
#   make migrate / makemigration MIG_MSG="add email" / alembic-current / alembic-history
#   make test / health / ready / live
#   make seed SEED_FILE="kit-staff/workmate_employees_basic.json"

SHELL := /bin/sh

# ---- Config ----
COMPOSE ?= docker compose
PROFILE ?= dev
ENV     ?= .env.dev

BACKEND_SVC  ?= backend
FRONTEND_SVC ?= ui
DB_SVC       ?= db
ADMINER_SVC  ?= adminer

SEED_FILE ?= kit-staff/workmate_employees_basic.json

# Helper: run compose with profile + env file wired in
CMD = ENV_FILE=$(ENV) $(COMPOSE) --profile $(PROFILE)

# Git SHA (short) for ENV stamping (optional)
SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo dev)

.PHONY: help
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | sed 's/:.*##/: /' | sort

# ---- Metadata helpers ----
.PHONY: sha
sha: ## Set GIT_SHA in $(ENV) to current commit
	@if [ -f "$(ENV)" ]; then \
	  if grep -q '^GIT_SHA=' "$(ENV)"; then sed -i 's/^GIT_SHA=.*/GIT_SHA=$(SHA)/' "$(ENV)"; \
	  else printf "\nGIT_SHA=$(SHA)\n" >> "$(ENV)"; fi; \
	else printf "APP_VERSION=0.1.0\nGIT_SHA=$(SHA)\n" > "$(ENV)"; fi; \
	echo "GIT_SHA=$(SHA)"

# ---- Stack controls ----
.PHONY: up
up: sha ## Start stack (no rebuild)
	$(CMD) up -d

.PHONY: down
down: ## Stop stack (keep volumes)
	$(CMD) down

.PHONY: restart
restart: ## Restart backend+ui
	$(CMD) restart $(BACKEND_SVC) $(FRONTEND_SVC)

.PHONY: ps
ps: ## Show container status
	$(CMD) ps

# ---- Logs / restarts ----
.PHONY: be-logs
be-logs: ## Tail backend logs
	$(CMD) logs -f $(BACKEND_SVC)

.PHONY: fe-logs
fe-logs: ## Tail frontend logs
	$(CMD) logs -f $(FRONTEND_SVC)

.PHONY: be-restart
be-restart: ## Restart backend only
	$(CMD) restart $(BACKEND_SVC)

.PHONY: fe-restart
fe-restart: ## Restart frontend only
	$(CMD) restart $(FRONTEND_SVC)

# ---- Rebuilds (only when Dockerfile/locks changed) ----
.PHONY: rebuild-ui
rebuild-ui: ## Rebuild UI image only
	$(CMD) up -d --build $(FRONTEND_SVC)

.PHONY: rebuild-be
rebuild-be: ## Rebuild backend image only
	$(CMD) up -d --build $(BACKEND_SVC)

# ---- Alembic & DB helpers ----
.PHONY: migrate
migrate: ## alembic upgrade head
	$(CMD) exec $(BACKEND_SVC) alembic upgrade head

.PHONY: makemigration
makemigration: ## autogen migration (MIG_MSG="message")
	@test -n "$(MIG_MSG)" || (echo 'Bitte MIG_MSG="..." setzen' && exit 1)
	$(CMD) exec $(BACKEND_SVC) alembic revision --autogenerate -m "$(MIG_MSG)"

.PHONY: alembic-current
alembic-current: ## show current revision
	$(CMD) exec $(BACKEND_SVC) alembic current

.PHONY: alembic-history
alembic-history: ## show history (verbose)
	$(CMD) exec $(BACKEND_SVC) alembic history --verbose

.PHONY: seed
seed: ## seed DB (override with SEED_FILE=...)
	$(CMD) exec $(BACKEND_SVC) python kit-staff/seed_kit_team.py --file $(SEED_FILE)

# ---- Health shortcuts ----
.PHONY: health
health: ## GET /api/health (via host)
	@curl -s http://localhost:8000/api/health | jq .

.PHONY: ready
ready: ## GET /api/ready (status code)
	@curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/ready

.PHONY: live
live: ## GET /api/live
	@curl -s http://localhost:8000/api/live | jq .

# ---- Tests ----
.PHONY: test
test: ## run pytest in backend container
	$(CMD) exec $(BACKEND_SVC) pytest -q || true
	
.PHONY: prod-up prod-down
prod-up: ## Build & start production stack
	ENV_FILE=.env.prod docker compose -f docker-compose.prod.yml up -d --build

prod-down: ## Stop production stack
	ENV_FILE=.env.prod docker compose -f docker-compose.prod.yml down
