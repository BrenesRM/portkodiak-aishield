"""
Database configuration and session management.
"""
import logging
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.common.models import Base

logger = logging.getLogger(__name__)

# Ensure data directory exists
try:
    settings.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
except PermissionError:
    logger.warning("Could not create DB directory, falling back to in-memory DB")
    settings.DB_PATH = ":memory:"

DATABASE_URL = f"sqlite:///{settings.DB_PATH}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Initialize the database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def get_db():
    """Dependency for obtaining a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> bool:
    """Verify database connectivity."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
