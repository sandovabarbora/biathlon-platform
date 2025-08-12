#!/bin/bash

echo "🎿 Starting Biathlon Pro in development mode..."

# Activate virtual environment
source .venv/bin/activate

# Run with auto-reload
uv run uvicorn biathlon_app.main:app --reload --host 0.0.0.0 --port 8000
