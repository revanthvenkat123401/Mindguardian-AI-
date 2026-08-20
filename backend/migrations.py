"""Database migration initialization script"""
from alembic import command
from alembic.config import Config
from database import engine
from models import Base
import os
import logging

logger = logging.getLogger(__name__)


def create_migrations():
    """Create initial migration"""
    alembic_cfg = Config("alembic.ini")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise


if __name__ == "__main__":
    create_migrations()
