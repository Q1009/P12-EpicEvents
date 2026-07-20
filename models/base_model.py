from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

Base = declarative_base()

class Table(Base):
    """Table de test pour vérifier la connexion à la BDD."""
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, default="connexion_ok")
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)