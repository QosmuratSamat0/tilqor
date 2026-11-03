# Short commands for local development. Run `make` to see the list.
# Windows: install GNU make (`winget install ezwinports.make`); macOS / Linux: make is built in.

ifeq ($(OS),Windows_NT)
PY := .venv\Scripts\python.exe
else
PY := .venv/bin/python
endif

MANAGE := $(PY) src/backend/manage.py

.DEFAULT_GOAL := help
.PHONY: help setup up down db logs run migrate shell superuser lint migrations-check test check

help:
	@echo Setup
	@echo   make setup             create .venv and install backend dependencies
	@echo Docker
	@echo   make up                start PostgreSQL and the backend on :8000
	@echo   make down              stop the containers
	@echo   make db                start only PostgreSQL (for local run and tests)
	@echo   make logs              follow the backend container logs
	@echo Local backend
	@echo   make run               Django dev server on :8001
	@echo   make migrate           apply migrations
	@echo   make shell             Django shell
	@echo   make superuser         create an administrator
	@echo Checks (same as CI)
	@echo   make lint              ruff
	@echo   make migrations-check  fail if a model change has no migration
	@echo   make test              pytest
	@echo   make check             lint + migrations-check + test

setup:
	python -m venv .venv
	$(PY) -m pip install -r src/backend/requirements-dev.txt

up:
	docker compose up --build -d

down:
	docker compose down

db:
	docker compose up -d db

logs:
	docker compose logs -f backend

run:
	$(MANAGE) runserver 8001

migrate:
	$(MANAGE) migrate

shell:
	$(MANAGE) shell

superuser:
	$(MANAGE) createsuperuser

lint:
	$(PY) -m ruff check src/backend tests

migrations-check:
	$(MANAGE) makemigrations --check --dry-run

test:
	$(PY) -m pytest -q

check: lint migrations-check test
