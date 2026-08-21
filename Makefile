.PHONY: dev build test test-backend test-frontend lint migrate seed clean

dev:
	docker-compose up -d

build:
	docker-compose build

test: test-backend test-frontend

test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm test

lint:
	cd backend && ruff check . && flake8 .
	cd frontend && npm run lint

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.scripts.seed_themes

clean:
	docker-compose down -v --remove-orphans
