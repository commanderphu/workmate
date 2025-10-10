# ===== Workmate Dev Makefile (clean) =====
# Usage:
#   make help
#   make up / down / restart / ps / logs
#   make db / db-clean
#   make be / fe / be-sh / fe-sh / psql
#   make migrate / makemigration MIG_MSG="add email" / alembic-current / alembic-history
#   make seed SEED_FILE="kit-staff/workmate_employees_basic.json"
#   make test / fmt / ci / build-be
#   make health

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

# Internal helper
CMD = ENV_FILE=$(ENV) $(COMPOSE) --profile $(PROFILE)

# Current short git sha (host)
SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo dev)

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | sed 's/:.*##/: /' | sort

# ---- Metadata helpers ----
.PHONY: sha
sha: ## Set GIT_SHA=<short> inside $(ENV)
	@if [ -f "$(ENV)" ]; then \
		if grep -q '^GIT_SHA=' "$(ENV)"; then \
			sed -i 's/^GIT_SHA=.*/GIT_SHA=$(SHA)/' "$(ENV)"; \
		else \
			printf "\nGIT_SHA=$(SHA)\n" >> "$(ENV)"; \
		fi; \
	else \
		printf "APP_VERSION=0.1.0\nGIT_SHA=$(SHA)\n" > "$(ENV)"; \
	fi
	@echo "GIT_SHA set to $(SHA) in $(ENV)"

.PHONY: set-version
set-version: ## Set APP_VERSION (use: make set-version VERSION=0.2.0)
	@test -n "$(VERSION)" || (echo 'Bitte VERSION="x.y.z" setzen' && exit 1)
	@if [ -f "$(ENV)" ]; then \
		if grep -q '^APP_VERSION=' "$(ENV)"; then \
			sed -i 's/^APP_VERSION=.*/APP_VERSION=$(VERSION)/' "$(ENV)"; \
		else \
			printf "\nAPP_VERSION=$(VERSION)\n" >> "$(ENV)"; \
		fi; \
	else \
		printf "APP_VERSION=$(VERSION)\nGIT_SHA=$(SHA)\n" > "$(ENV)"; \
	fi
	@echo "APP_VERSION set to $(VERSION) in $(ENV)"

# ---- Stack ----
.PHONY: up
up: sha ## Start all services (detached) after setting GIT_SHA
	$(CMD) up -d --build

.PHONY: down
down: ## Stop all services (keep volumes)
	$(CMD) down

.PHONY: restart
restart: ## Restart all services
	$(CMD) down && $(CMD) up -d --build

.PHONY: ps
ps: ## Show service status
	$(CMD) ps

.PHONY: logs
logs: ## Tail logs (use SVC=<name>, default=$(BACKEND_SVC))
	$(CMD) logs -f $${SVC:-$(BACKEND_SVC)} --tail=100

# ---- Partial starts ----
.PHONY: db
db: ## Start DB + Adminer only
	$(CMD) up -d $(DB_SVC) $(ADMINER_SVC)

.PHONY: db-clean
db-clean: ## ⚠️ Stop stack & remove volumes (fresh DB)
	$(CMD) down -v

.PHONY: be
be: ## Run backend in foreground (debug)
	$(CMD) up $(BACKEND_SVC)

.PHONY: fe
fe: ## Run frontend in foreground
	$(CMD) up $(FRONTEND_SVC)

# ---- Alembic ----
.PHONY: migrate
migrate: ## alembic upgrade head
	$(CMD) run --rm $(BACKEND_SVC) alembic upgrade head

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

# ---- Seeds & DB tools ----
.PHONY: seed
seed: ## seed DB (SEED_FILE overrideable)
	$(CMD) exec $(BACKEND_SVC) python kit-staff/seed_kit_team.py --file $(SEED_FILE)

.PHONY: psql
psql: ## open psql in DB container (uses POSTGRES_* env in container)
	$(CMD) exec -e PGPASSWORD=$$POSTGRES_PASSWORD $(DB_SVC) \
	sh -lc 'psql -h localhost -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

# ---- Shells ----
.PHONY: be-sh
be-sh: ## shell into backend
	$(CMD) exec $(BACKEND_SVC) sh

.PHONY: fe-sh
fe-sh: ## shell into frontend
	$(CMD) exec $(FRONTEND_SVC) sh

# ---- Tests & Format ----
.PHONY: test
test: ## run pytest in backend (if installed)
	$(CMD) exec $(BACKEND_SVC) pytest -q || true

.PHONY: fmt
fmt: ## run black/isort/ruff if available
	$(CMD) exec $(BACKEND_SVC) sh -lc 'black app || true; isort app || true; ruff check app --fix || true'

# ---- Local CI mimic & build ----
.PHONY: ci
ci: ## DB -> migrate -> pytest (quick local CI)
	$(CMD) up -d $(DB_SVC)
	sleep 3
	$(CMD) exec $(BACKEND_SVC) alembic upgrade head
	$(CMD) exec $(BACKEND_SVC) pytest -q || true

.PHONY: build-be
build-be: ## build backend dev image
	docker build -f backend/Dockerfile.dev -t workmate/backend:dev ./backend

# ---- Convenience ----
.PHONY: health live ready
health:
	@curl -s http://localhost:8000/api/health | jq .
live:
	@curl -s http://localhost:8000/api/live | jq .
ready:
	@curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/ready

