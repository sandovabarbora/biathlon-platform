#!/bin/bash

echo "🎿 Starting Biathlon Pro in production mode..."

# Activate virtual environment
source .venv/bin/activate

# Run with gunicorn
uv run gunicorn biathlon_app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --log-level info
