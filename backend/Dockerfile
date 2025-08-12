FROM python:3.11-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY app/ ./app/

# Install dependencies with uv
RUN uv venv && \
    uv pip install -e .

# Run with uv
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
