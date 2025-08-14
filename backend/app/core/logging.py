"""Structured logging configuration"""
import logging
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Any, Dict

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
            
        return json.dumps(log_obj)


def setup_logging() -> None:
    """Configure application logging"""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler for production
    if settings.is_production:
        file_handler = logging.FileHandler("app.log")
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    
    # Set specific log levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Log startup info
    root_logger.info(
        "Logging configured",
        extra={
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "log_level": logging.getLevelName(log_level)
        }
    )
