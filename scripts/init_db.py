#!/usr/bin/env python3
"""
Database initialization script
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.database.session import engine
from app.database import models
from app.core.logging import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)


def init_database():
    try:
        logger.info("Creating database tables...")
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
