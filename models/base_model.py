from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Table(Base):
    """Test table to check database connection."""
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, default="connexion_ok")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)