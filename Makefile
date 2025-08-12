# ==========================================
# 🎿 BIATHLON ANALYTICS - Makefile
# ==========================================

.PHONY: help setup install run dev backend frontend test clean reset docker lint format check

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)🎿 BIATHLON ANALYTICS PLATFORM$(NC)"
	@echo "================================"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start:"
	@echo "  $$ make setup"
	@echo "  $$ make run"

# ==================== SETUP ====================

setup: ## Complete initial setup
	@echo "$(BLUE)🚀 Running complete setup...$(NC)"
	@./setup.sh
	@echo "$(GREEN)✅ Setup complete!$(NC)"

install: ## Install/update dependencies
	@echo "$(BLUE)📦 Installing dependencies...$(NC)"
	@cd backend && uv pip sync requirements.txt
	@cd frontend && npm install
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

install-dev: ## Install with dev dependencies
	@echo "$(BLUE)📦 Installing dev dependencies...$(NC)"
	@cd backend && source .venv/bin/activate && uv pip install -e ".[dev]"
	@cd frontend && npm install --include=dev
	@echo "$(GREEN)✅ Dev dependencies installed$(NC)"

# ==================== RUNNING ====================

run: ## Run full application (backend + frontend)
	@echo "$(BLUE)🎿 Starting Biathlon Analytics...$(NC)"
	@./run.sh

dev: run ## Alias for run

backend: ## Run backend only
	@echo "$(BLUE)🐍 Starting backend...$(NC)"
	@cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Run frontend only
	@echo "$(BLUE)⚛️ Starting frontend...$(NC)"
	@cd frontend && npm run dev

worker: ## Run background worker (if needed)
	@echo "$(BLUE)⚙️ Starting worker...$(NC)"
	@cd backend && source .venv/bin/activate && python -m app.worker

# ==================== TESTING ====================

test: ## Run all tests
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@make test-backend
	@make test-frontend
	@echo "$(GREEN)✅ All tests passed$(NC)"

test-backend: ## Run backend tests
	@echo "$(BLUE)Testing backend...$(NC)"
	@cd backend && source .venv/bin/activate && pytest tests/ -v

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Testing frontend...$(NC)"
	@cd frontend && npm test

test-coverage: ## Run tests with coverage
	@echo "$(BLUE)📊 Running tests with coverage...$(NC)"
	@cd backend && source .venv/bin/activate && pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report: backend/htmlcov/index.html$(NC)"

test-watch: ## Run tests in watch mode
	@cd backend && source .venv/bin/activate && pytest-watch

# ==================== CODE QUALITY ====================

lint: ## Run linters
	@echo "$(BLUE)🔍 Running linters...$(NC)"
	@cd backend && source .venv/bin/activate && ruff check app/ tests/
	@cd frontend && npm run lint
	@echo "$(GREEN)✅ Linting complete$(NC)"

format: ## Format code
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	@cd backend && source .venv/bin/activate && black app/ tests/ && ruff check --fix app/ tests/
	@echo "$(GREEN)✅ Code formatted$(NC)"

check: lint test ## Run all checks (lint + test)
	@echo "$(GREEN)✅ All checks passed$(NC)"

type-check: ## Run type checking
	@echo "$(BLUE)🔍 Type checking...$(NC)"
	@cd backend && source .venv/bin/activate && mypy app/

# ==================== DATABASE ====================

db-migrate: ## Run database migrations
	@echo "$(BLUE)🗄️ Running migrations...$(NC)"
	@cd backend && source .venv/bin/activate && alembic upgrade head

db-rollback: ## Rollback last migration
	@echo "$(YELLOW)⏪ Rolling back migration...$(NC)"
	@cd backend && source .venv/bin/activate && alembic downgrade -1

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "$(RED)⚠️  WARNING: This will delete all data!$(NC)"
	@echo "Press Ctrl+C to cancel, or wait 3 seconds..."
	@sleep 3
	@cd backend && source .venv/bin/activate && alembic downgrade base && alembic upgrade head
	@echo "$(GREEN)✅ Database reset$(NC)"

db-seed: ## Seed database with sample data
	@echo "$(BLUE)🌱 Seeding database...$(NC)"
	@cd backend && source .venv/bin/activate && python -m app.scripts.seed_db
	@echo "$(GREEN)✅ Database seeded$(NC)"

# ==================== DOCKER ====================

docker-build: ## Build Docker images
	@echo "$(BLUE)🐳 Building Docker images...$(NC)"
	@docker-compose build
	@echo "$(GREEN)✅ Images built$(NC)"

docker-up: ## Start Docker containers
	@echo "$(BLUE)🐳 Starting containers...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✅ Containers started$(NC)"

docker-down: ## Stop Docker containers
	@echo "$(YELLOW)Stopping containers...$(NC)"
	@docker-compose down

docker-logs: ## Show Docker logs
	@docker-compose logs -f

docker-clean: ## Clean Docker resources
	@echo "$(YELLOW)🧹 Cleaning Docker resources...$(NC)"
	@docker-compose down -v
	@docker system prune -f

# ==================== UTILITIES ====================

clean: ## Clean cache and temporary files
	@echo "$(YELLOW)🧹 Cleaning cache files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf backend/.coverage backend/htmlcov
	@rm -rf frontend/dist frontend/build
	@echo "$(GREEN)✅ Cleaned$(NC)"

reset: clean ## Full reset (clean + remove venv & node_modules)
	@echo "$(RED)🔄 Full reset...$(NC)"
	@rm -rf backend/.venv
	@rm -rf frontend/node_modules
	@echo "$(GREEN)✅ Reset complete. Run 'make setup' to reinstall$(NC)"

logs: ## Show application logs
	@echo "$(BLUE)📋 Showing logs...$(NC)"
	@tail -f backend/logs/app.log

shell: ## Open Python shell with app context
	@cd backend && source .venv/bin/activate && python -m IPython

repl: shell ## Alias for shell

# ==================== DEPLOYMENT ====================

build: ## Build for production
	@echo "$(BLUE)📦 Building for production...$(NC)"
	@cd frontend && npm run build
	@cd backend && source .venv/bin/activate && python -m build
	@echo "$(GREEN)✅ Build complete$(NC)"

deploy-staging: ## Deploy to staging
	@echo "$(BLUE)🚀 Deploying to staging...$(NC)"
	@echo "TODO: Add staging deployment"

deploy-production: ## Deploy to production
	@echo "$(RED)🚀 Deploying to PRODUCTION...$(NC)"
	@echo "Are you sure? [y/N]" && read ans && [ $${ans:-N} = y ]
	@echo "TODO: Add production deployment"

# ==================== DEVELOPMENT TOOLS ====================

new-migration: ## Create new database migration
	@echo "$(BLUE)Creating new migration...$(NC)"
	@read -p "Migration name: " name; \
	cd backend && source .venv/bin/activate && alembic revision --autogenerate -m "$$name"

api-docs: ## Open API documentation
	@echo "$(BLUE)Opening API docs...$(NC)"
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs

tunnel: ## Create ngrok tunnel (for testing)
	@echo "$(BLUE)Creating tunnel...$(NC)"
	@ngrok http 8000

monitor: ## Open monitoring dashboard
	@echo "$(BLUE)Opening monitoring...$(NC)"
	@open http://localhost:3000/admin

# ==================== GIT HELPERS ====================

commit: format lint ## Format, lint, then commit
	@git add -A && git commit

push: check ## Run checks then push
	@git push

pr: check ## Create pull request
	@gh pr create

.PHONY: all $(MAKECMDGOALS)
