# ==========================================
# 🎿 BIATHLON APP - Makefile
# ==========================================

.PHONY: help install install-dev install-all clean test run dev prod format lint check docs

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(BLUE)🎿 BIATHLON APP - Available commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quick start:$(NC)"
	@echo "  make install     - Install core dependencies"
	@echo "  make dev        - Run in development mode"
	@echo ""

# ==================== INSTALLATION ====================

install: ## Install core dependencies with UV
	@echo "$(BLUE)📦 Installing core dependencies...$(NC)"
	@command -v uv >/dev/null 2>&1 || { echo "$(RED)UV not found. Installing...$(NC)"; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@uv venv || true
	@uv pip install -e .
	@echo "$(GREEN)✅ Core dependencies installed$(NC)"

install-dev: install ## Install with development dependencies
	@echo "$(BLUE)📦 Installing development dependencies...$(NC)"
	@uv pip install -e ".[dev]"
	@echo "$(GREEN)✅ Development dependencies installed$(NC)"

install-ml: install ## Install with ML dependencies
	@echo "$(BLUE)📦 Installing ML dependencies...$(NC)"
	@uv pip install -e ".[ml]"
	@echo "$(GREEN)✅ ML dependencies installed$(NC)"

install-all: ## Install all dependencies
	@echo "$(BLUE)📦 Installing all dependencies...$(NC)"
	@uv venv || true
	@uv pip install -e ".[dev,ml,viz,prod]"
	@echo "$(GREEN)✅ All dependencies installed$(NC)"

update: ## Update all dependencies
	@echo "$(BLUE)📦 Updating dependencies...$(NC)"
	@uv pip install --upgrade -e .
	@echo "$(GREEN)✅ Dependencies updated$(NC)"

# ==================== DEVELOPMENT ====================

run: ## Run the application
	@echo "$(BLUE)🚀 Starting Biathlon App...$(NC)"
	@uv run python -m biathlon_app.main

dev: ## Run in development mode with auto-reload
	@echo "$(BLUE)🚀 Starting in development mode...$(NC)"
	@uv run uvicorn biathlon_app.main:app --reload --host 0.0.0.0 --port 8000

prod: ## Run in production mode with gunicorn
	@echo "$(BLUE)🚀 Starting in production mode...$(NC)"
	@uv run gunicorn biathlon_app.main:app \
		--workers 4 \
		--worker-class uvicorn.workers.UvicornWorker \
		--bind 0.0.0.0:8000 \
		--log-level info

debug: ## Run with debug logging
	@echo "$(BLUE)🐛 Starting with debug logging...$(NC)"
	@LOG_LEVEL=DEBUG uv run python -m biathlon_app.main

# ==================== TESTING ====================

test: ## Run all tests
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@uv run pytest tests/ -v

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)🧪 Running tests with coverage...$(NC)"
	@uv run pytest tests/ -v --cov=biathlon_app --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/index.html$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)🧪 Running tests in watch mode...$(NC)"
	@uv run ptw tests/

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(NC)"
	@uv run pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)🧪 Running integration tests...$(NC)"
	@uv run pytest tests/integration/ -v

# ==================== CODE QUALITY ====================

format: ## Format code with black and ruff
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	@uv run black src/ tests/
	@uv run ruff check --fix src/ tests/
	@echo "$(GREEN)✅ Code formatted$(NC)"

lint: ## Run linting checks
	@echo "$(BLUE)🔍 Running linters...$(NC)"
	@uv run ruff check src/ tests/
	@uv run mypy src/
	@echo "$(GREEN)✅ Linting complete$(NC)"

check: lint test ## Run all checks (lint + test)
	@echo "$(GREEN)✅ All checks passed$(NC)"

clean-pyc: ## Remove Python cache files
	@echo "$(BLUE)🧹 Cleaning Python cache...$(NC)"
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -delete
	@find . -type d -name '.pytest_cache' -delete
	@find . -type d -name '.mypy_cache' -delete
	@echo "$(GREEN)✅ Python cache cleaned$(NC)"

# ==================== DATABASE ====================

db-init: ## Initialize database
	@echo "$(BLUE)🗄️ Initializing database...$(NC)"
	@uv run python -m biathlon_app.data.init_db
	@echo "$(GREEN)✅ Database initialized$(NC)"

db-migrate: ## Run database migrations
	@echo "$(BLUE)🗄️ Running migrations...$(NC)"
	@uv run alembic upgrade head
	@echo "$(GREEN)✅ Migrations complete$(NC)"

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)⚠️  WARNING: This will destroy all data!$(NC)"
	@echo "Press Ctrl+C to cancel, or wait 3 seconds..."
	@sleep 3
	@uv run python -m biathlon_app.data.reset_db
	@echo "$(GREEN)✅ Database reset$(NC)"

# ==================== DATA MANAGEMENT ====================

data-load: ## Load sample data
	@echo "$(BLUE)📊 Loading sample data...$(NC)"
	@uv run python -m biathlon_app.data.load_samples
	@echo "$(GREEN)✅ Sample data loaded$(NC)"

data-fetch: ## Fetch latest IBU data
	@echo "$(BLUE)📊 Fetching latest IBU data...$(NC)"
	@uv run python -m biathlon_app.data.fetch_ibu
	@echo "$(GREEN)✅ Data fetched$(NC)"

data-export: ## Export data to CSV
	@echo "$(BLUE)📊 Exporting data...$(NC)"
	@uv run python -m biathlon_app.data.export --format csv --output exports/
	@echo "$(GREEN)✅ Data exported to exports/$(NC)"

# ==================== DOCUMENTATION ====================

docs: ## Generate documentation
	@echo "$(BLUE)📚 Generating documentation...$(NC)"
	@uv run mkdocs build
	@echo "$(GREEN)✅ Documentation built in site/$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)📚 Serving documentation...$(NC)"
	@uv run mkdocs serve

api-docs: ## Open API documentation in browser
	@echo "$(BLUE)📚 Opening API docs...$(NC)"
	@python -m webbrowser http://localhost:8000/docs

# ==================== DOCKER ====================

docker-build: ## Build Docker image
	@echo "$(BLUE)🐳 Building Docker image...$(NC)"
	@docker build -t biathlon-app:latest .
	@echo "$(GREEN)✅ Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(BLUE)🐳 Running Docker container...$(NC)"
	@docker run -p 8000:8000 -v $(PWD)/data:/app/data biathlon-app:latest

docker-compose-up: ## Start with docker-compose
	@echo "$(BLUE)🐳 Starting services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✅ Services started$(NC)"

docker-compose-down: ## Stop docker-compose services
	@echo "$(BLUE)🐳 Stopping services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✅ Services stopped$(NC)"

# ==================== UTILITIES ====================

shell: ## Open Python shell with app context
	@echo "$(BLUE)🐍 Opening Python shell...$(NC)"
	@uv run ipython

jupyter: ## Start Jupyter notebook
	@echo "$(BLUE)📓 Starting Jupyter...$(NC)"
	@uv run jupyter notebook

clean: clean-pyc ## Clean all temporary files
	@echo "$(BLUE)🧹 Cleaning temporary files...$(NC)"
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info
	@rm -rf .ruff_cache/
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

reset: clean ## Full reset (clean + remove venv)
	@echo "$(RED)⚠️  Removing virtual environment...$(NC)"
	@rm -rf .venv/
	@echo "$(GREEN)✅ Full reset complete$(NC)"

version: ## Show version
	@echo "$(BLUE)Biathlon App Version:$(NC)"
	@uv run python -c "from biathlon_app import __version__; print(__version__)"

# ==================== CI/CD ====================

ci: install-dev lint test ## Run CI pipeline
	@echo "$(GREEN)✅ CI pipeline passed$(NC)"

pre-commit: format lint test ## Run pre-commit checks
	@echo "$(GREEN)✅ Ready to commit$(NC)"

release: check ## Create a new release
	@echo "$(BLUE)📦 Creating release...$(NC)"
	@uv run python -m build
	@echo "$(GREEN)✅ Release created in dist/$(NC)"

# ==================== MONITORING ====================

logs: ## Show application logs
	@echo "$(BLUE)📋 Application logs:$(NC)"
	@tail -f logs/biathlon.log

stats: ## Show application statistics
	@echo "$(BLUE)📊 Application statistics:$(NC)"
	@uv run python -m biathlon_app.utils.stats

health: ## Check application health
	@echo "$(BLUE)🏥 Health check:$(NC)"
	@curl -s http://localhost:8000/health | python -m json.tool

# ==================== SHORTCUTS ====================

i: install        ## Shortcut for install
d: dev           ## Shortcut for dev
t: test          ## Shortcut for test
f: format        ## Shortcut for format
l: lint          ## Shortcut for lint
c: clean         ## Shortcut for clean