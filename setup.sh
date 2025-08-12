#!/bin/bash

# ==========================================
# 🎿 BIATHLON APP - UV Setup & Installation
# ==========================================

echo "🎿 BIATHLON APP - UV Installation"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ==================== INSTALL UV ====================
install_uv() {
    if ! command -v uv &> /dev/null; then
        echo -e "${YELLOW}📦 Installing UV package manager...${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Add to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"

        # Add to shell config
        if [ -f "$HOME/.bashrc" ]; then
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$HOME/.bashrc"
        fi
        if [ -f "$HOME/.zshrc" ]; then
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$HOME/.zshrc"
        fi

        echo -e "${GREEN}✅ UV installed successfully${NC}"
    else
        echo -e "${GREEN}✅ UV is already installed${NC}"
    fi
}

# ==================== CREATE PROJECT STRUCTURE ====================
create_structure() {
    echo -e "${BLUE}📁 Creating project structure...${NC}"

    # Create directories
    mkdir -p src/biathlon_app/{api,analytics,data,models,utils}
    mkdir -p tests/{unit,integration}
    mkdir -p data
    mkdir -p docs
    mkdir -p scripts

    # Create __init__.py files
    touch src/biathlon_app/__init__.py
    touch src/biathlon_app/api/__init__.py
    touch src/biathlon_app/analytics/__init__.py
    touch src/biathlon_app/data/__init__.py
    touch src/biathlon_app/models/__init__.py
    touch src/biathlon_app/utils/__init__.py

    echo -e "${GREEN}✅ Project structure created${NC}"
}

# ==================== CREATE PYPROJECT.TOML ====================
# ==================== INSTALL WITH UV ====================
install_dependencies() {
    echo -e "${BLUE}📦 Installing dependencies with UV...${NC}"

    # Create virtual environment
    uv venv

    # Install project in editable mode with all dependencies
    uv pip install -e .

    # Install optional dependencies
    echo -e "${YELLOW}Install optional dependencies? (dev/ml/all/none): ${NC}"
    read -r optional_deps

    case $optional_deps in
        dev)
            uv pip install -e ".[dev]"
            echo -e "${GREEN}✅ Dev dependencies installed${NC}"
            ;;
        ml)
            uv pip install -e ".[ml]"
            echo -e "${GREEN}✅ ML dependencies installed${NC}"
            ;;
        all)
            uv pip install -e ".[dev,ml]"
            echo -e "${GREEN}✅ All optional dependencies installed${NC}"
            ;;
        *)
            echo "Skipping optional dependencies"
            ;;
    esac
}

# ==================== CREATE ENV FILE ====================
create_env_file() {
    echo -e "${BLUE}🔧 Creating .env file...${NC}"

    cat > .env << 'EOF'
# Biathlon App Configuration
APP_NAME=Biathlon Pro
APP_VERSION=1.0.0
DEBUG=True

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Data Configuration
DATA_DIR=./data
CACHE_DIR=./cache

# Database (optional)
# DATABASE_URL=postgresql://user:pass@localhost/biathlon

# Redis (optional)
# REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/biathlon.log

# Security
# SECRET_KEY=your-secret-key-here
# ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Features
ENABLE_ML_FEATURES=False
ENABLE_CACHE=True
CACHE_TTL=3600

# External APIs (if needed)
# IBU_API_KEY=your-api-key
# WEATHER_API_KEY=your-api-key
EOF

    echo -e "${GREEN}✅ .env file created${NC}"
}

# ==================== CREATE SAMPLE FILES ====================
create_sample_files() {
    echo -e "${BLUE}📝 Creating sample application files...${NC}"

    # Main application file
    cat > src/biathlon_app/main.py << 'EOF'
"""
Biathlon Pro - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from biathlon_app.api import routes
from biathlon_app.data import loader
from biathlon_app.utils import config

# Setup logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🎿 Starting Biathlon Pro...")
    # Load data on startup
    loader.load_all_data()
    yield
    logger.info("👋 Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Biathlon Pro",
    description="Professional Analytics Platform for Biathlon Coaches",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Biathlon Pro",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "biathlon_app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )
EOF

    # Config file
    cat > src/biathlon_app/utils/config.py << 'EOF'
"""
Configuration management
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# App settings
APP_NAME = os.getenv("APP_NAME", "Biathlon Pro")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
CACHE_DIR = Path(os.getenv("CACHE_DIR", PROJECT_ROOT / "cache"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True, parents=True)
CACHE_DIR.mkdir(exist_ok=True, parents=True)
EOF

    echo -e "${GREEN}✅ Sample files created${NC}"
}

# ==================== CREATE RUN SCRIPTS ====================
create_run_scripts() {
    echo -e "${BLUE}🚀 Creating run scripts...${NC}"

    # Development run script
    cat > run_dev.sh << 'EOF'
#!/bin/bash

echo "🎿 Starting Biathlon Pro in development mode..."

# Activate virtual environment
source .venv/bin/activate

# Run with auto-reload
uv run uvicorn biathlon_app.main:app --reload --host 0.0.0.0 --port 8000
EOF
    chmod +x run_dev.sh

    # Production run script
    cat > run_prod.sh << 'EOF'
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
EOF
    chmod +x run_prod.sh

    # Test run script
    cat > run_tests.sh << 'EOF'
#!/bin/bash

echo "🧪 Running tests..."

# Activate virtual environment
source .venv/bin/activate

# Run tests with coverage
uv run pytest tests/ -v --cov=biathlon_app --cov-report=term-missing
EOF
    chmod +x run_tests.sh

    echo -e "${GREEN}✅ Run scripts created${NC}"
}

# ==================== MAIN INSTALLATION ====================
main() {
    echo -e "${BLUE}Starting Biathlon App installation...${NC}"
    echo ""

    # Step 1: Install UV
    install_uv

    # Step 2: Create project structure
    create_structure

    # Step 3: Create pyproject.toml
    create_pyproject

    # Step 4: Install dependencies
    install_dependencies

    # Step 5: Create env file
    create_env_file

    # Step 6: Create sample files
    create_sample_files

    # Step 7: Create run scripts
    create_run_scripts

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✅ BIATHLON APP INSTALLATION COMPLETE!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "📁 Project structure:"
    echo "   src/biathlon_app/  - Main application code"
    echo "   tests/             - Test files"
    echo "   data/              - Data directory"
    echo "   .venv/             - Virtual environment"
    echo ""
    echo "🚀 Quick start:"
    echo "   Development:  ./run_dev.sh"
    echo "   Production:   ./run_prod.sh"
    echo "   Tests:        ./run_tests.sh"
    echo ""
    echo "📦 Installed packages:"
    echo "   Core:     FastAPI, Pandas, NumPy"
    echo "   Optional: Run 'uv pip install -e .[dev,ml]' for extras"
    echo ""
    echo "📚 Documentation:"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   README:   cat README.md"
    echo ""
    echo "🎿 Happy coding!"
}

# Run main installation
main
EOF