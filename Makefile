ifneq (,$(wildcard .env))
include .env
export
endif

TAIL = 100
BASE_COMPOSE_PROJECT_NAME = oba_task
TEST_COMPOSE_PROJECT_NAME = oba_task_test

DATABASE_URL ?= postgresql+psycopg://postgres:postgres@localhost:5432/oba
TEST_DATABASE_URL ?= postgresql+psycopg://postgres:postgres@localhost:5432/oba_test

define set-default-container
	ifndef c
	c = api
	else ifeq (${c},all)
	override c =
	endif
endef

set-container:
	$(eval $(call set-default-container))

.PHONY: up down logs restart migrate migration-create app-shell db-shell test ruff-check ruff-format set-container

up:
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml up --build -d

down:
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml down

logs: set-container
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml logs --tail=$(TAIL) -f $(c)

restart: set-container
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml restart $(c)

migrate:
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml exec api uv run python -m alembic upgrade head

migration-create:
	@test -n "$(strip $(message))" || (echo 'Usage: make migration-create message="describe changes"' >&2; exit 1)
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml exec api uv run python -m alembic revision --autogenerate -m "$(message)"

app-shell:
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml exec api /bin/sh

db-shell:
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml exec db psql -U postgres -d oba

test:
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml up -d db
	DATABASE_URL=$(TEST_DATABASE_URL) uv run reset-postgres-db
	DATABASE_URL=$(TEST_DATABASE_URL) uv run python -m alembic upgrade head
	@status=0; \
	TEST_DATABASE_URL=$(TEST_DATABASE_URL) TEST_DB_PREPARED=1 uv run python -m pytest --no-header -v --tb=short -ra || status=$$?; \
	DATABASE_URL=$(TEST_DATABASE_URL) uv run drop-postgres-db; \
	exit $$status

ruff-check: set-container
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml exec $(c) /bin/sh -c 'uv run --group dev python -m ruff check'

ruff-format: set-container
	docker compose -p $(BASE_COMPOSE_PROJECT_NAME) -f docker-compose.yml exec $(c) /bin/sh -c 'uv run --group dev python -m ruff check --fix --unsafe-fixes && uv run --group dev python -m ruff format'
