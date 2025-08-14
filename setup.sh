#!/bin/bash

echo "🚀 Setting up Biathlon Digital Twin Development Environment..."

# Check prerequisites
command -v uv >/dev/null 2>&1 || { 
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
}

command -v node >/dev/null 2>&1 || { 
    echo "Node.js is required but not installed. Please install Node.js 20+" >&2; 
    exit 1; 
}

command -v docker >/dev/null 2>&1 || { 
    echo "Docker is required but not installed. Please install Docker" >&2; 
    exit 1; 
}

# Setup backend
echo "📦 Setting up backend with uv..."
cd backend
uv venv
source .venv/bin/activate
uv pip sync

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend
npm install

# Setup databases
echo "🐳 Starting databases..."
cd ..
docker-compose up -d postgres redis

# Wait for DB
echo "⏳ Waiting for database..."
sleep 5

# Create .env from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file from .env.example"
fi

echo "✅ Setup complete!"
echo ""
echo "To start development servers:"
echo "  make dev"
echo ""
echo "Or manually:"
echo "  Backend:  cd backend && uv run uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
