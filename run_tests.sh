#!/bin/bash

echo "🧪 Running tests..."

# Activate virtual environment
source .venv/bin/activate

# Run tests with coverage
uv run pytest tests/ -v --cov=biathlon_app --cov-report=term-missing
