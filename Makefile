ifeq (,$(wildcard ./.env))
    $(error Файл .env не найден. Создайте его из .env.LOCAL)
endif
include .env
export $(shell sed 's/=.*//' .env)

SH := /bin/bash
DOCKER_COMPOSE = docker compose
DOCKER = docker
EXEC = $(DOCKER) exec -i

TRUNCATE_FILE = ./env/pgsql/truncate.sql

FLYWAY_CONTAINER = cli-flyway
POSTGRES_CONTAINER = db

FLYWAY_DOCKER_RUN = $(DOCKER_COMPOSE) run --rm $(FLYWAY_CONTAINER)
FLYWAY_DB_URL = jdbc:postgresql://${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
FLYWAY_RUN = $(FLYWAY_DOCKER_RUN) -url=$(FLYWAY_DB_URL) -user=$(POSTGRES_USER) -password=$(POSTGRES_PASSWORD)



migrate:
	$(FLYWAY_RUN) migrate

drop:
	$(FLYWAY_RUN) -cleanDisabled=false clean

create:
	$(FLYWAY_RUN) migrate -target=1

recreate: drop create

reset: drop migrate


up-db:
	$(DOCKER_COMPOSE) up -d db

wait-db:
	@echo "⏳ Ожидание готовности базы данных..."
	@until $(DOCKER) exec koin-db-1 pg_isready -U $(POSTGRES_USER); do sleep 1; done
	@echo "✅ База данных готова!"

up-all:
	$(DOCKER_COMPOSE) up -d

init: up-db wait-db recreate up-all




help:
	@echo "Available commands:"
	@echo "  migrate    - Apply all pending database migrations"
	@echo "  drop       - Drop all tables"
	@echo "  create     - Create empty tables (won't work if tables already populated)"
	@echo "  recreate   - Drop and recreate empty tables"
	@echo "  truncate   - Truncate tables preserving their structure"
	@echo "  reset      - Clean and repopulate tables"
	@echo "  up-db      - Start only the database container"
	@echo "  wait-db    - Wait until the database is ready"
	@echo "  up-all     - Start all containers"
	@echo "  init       - Full setup: db -> migrations -> full system"
	@echo "  help       - Show this help message"

.PHONY: migrate drop create recreate truncate reset help up-db wait-db up-all init
