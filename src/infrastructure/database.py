"""
Database Management with SQLAlchemy
"""
from typing import Optional, Generator
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, DateTime, JSON, Boolean
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from datetime import datetime
from src.config.settings import get_settings
from src.utilities.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Create base class for models
Base = declarative_base()
metadata = MetaData()


# Define tables
assets_table = Table(
    'assets',
    metadata,
    Column('symbol', String, primary_key=True),
    Column('name', String),
    Column('asset_type', String),
    Column('base_currency', String, nullable=True),
    Column('quote_currency', String, nullable=True),
    Column('exchange', String, nullable=True),
    Column('is_active', Boolean, default=True),
    Column('metadata', JSON),
    Column('created_at', DateTime, default=datetime.now),
    Column('updated_at', DateTime, default=datetime.now, onupdate=datetime.now)
)

market_data_table = Table(
    'market_data',
    metadata,
    Column('id', String, primary_key=True),
    Column('asset_symbol', String),
    Column('timestamp', DateTime),
    Column('price', Float),
    Column('volume', Float, nullable=True),
    Column('market_cap', Float, nullable=True),
    Column('change_24h', Float, nullable=True),
    Column('data', JSON),
    Column('created_at', DateTime, default=datetime.now)
)

analyses_table = Table(
    'analyses',
    metadata,
    Column('id', String, primary_key=True),
    Column('query', String),
    Column('asset_symbol', String),
    Column('outlook', String),
    Column('confidence', Float),
    Column('risk_level', String),
    Column('trading_action', String),
    Column('analysis_data', JSON),
    Column('created_at', DateTime, default=datetime.now)
)


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=settings.debug
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        logger.info(f"Database initialized: {self.database_url.split('@')[-1]}")
    
    def create_tables(self):
        """Create all tables"""
        try:
            metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[dict] = None):
        """Execute raw SQL query"""
        with self.get_session() as session:
            result = session.execute(query, params or {})
            return result.fetchall()
    
    def health_check(self) -> bool:
        """Check database health"""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False


# Global database instance
_db_manager: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Get database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session"""
    db = get_db()
    with db.get_session() as session:
        yield session