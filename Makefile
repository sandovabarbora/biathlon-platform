.PHONY: help install dev test clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make dev       - Start development servers"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Clean temporary files"
	@echo "  make docker-up - Start Docker services"
	@echo "  make docker-down - Stop Docker services"

install:
	@echo "Installing backend dependencies with uv..."
	cd backend && uv pip sync
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev:
	@echo "Starting development servers..."
	make docker-up
	cd backend && uv run uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev &

test:
	@echo "Running backend tests..."
	cd backend && uv run pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type d -name ".next" -exec rm -rf {} +

docker-up:
	docker-compose up -d postgres redis

docker-down:
	docker-compose down

format:
	cd backend && uv run ruff format .
	cd frontend && npx prettier --write .

lint:
	cd backend && uv run ruff check .
	cd backend && uv run mypy .
	cd frontend && npm run lint
