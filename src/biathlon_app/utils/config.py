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
