.PHONY: install dev run test clean

# Install dependencies with uv
install:
	uv venv
	uv pip install -e .

# Install with dev dependencies
dev:
	uv venv
	uv pip install -e ".[dev]"

# Run the application
run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	uv run pytest

# Clean up
clean:
	rm -rf .venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache

# Format code
format:
	uv run ruff format .

# Lint code  
lint:
	uv run ruff check .

# Update dependencies
update:
	uv pip compile pyproject.toml -o requirements.lock
	uv pip sync requirements.lock
