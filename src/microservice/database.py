import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define base directory and SQLite connection string
DATABASE_URL = "sqlite:///webhook_validator.db"

Base = declarative_base()

class WebhookDelivery(Base):
    """
    SQLAlchemy database model for storing incoming webhook payloads,
    source IP hashes, cryptographic signatures, and delivery validation statuses.
    """
    __tablename__ = "webhook_deliveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payload = Column(Text, nullable=False)
    source_ip_hash = Column(String(64), nullable=False, index=True)
    signature = Column(String(128), nullable=False)
    processing_status = Column(String(20), nullable=False, default="pending", index=True)
    delivered_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    # Explicit multi-column index for status checking by IP hash
    __table_args__ = (
        Index("idx_ip_hash_status", "source_ip_hash", "processing_status"),
    )

# Establish database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create thread-safe session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Initializes schema tables in the SQLite database."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Context manager helper for database session lifecycles."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
