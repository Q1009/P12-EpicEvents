from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from models.base_model import Base

# class User(Base):
#     """Table de test pour vérifier la connexion à la BDD."""
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, autoincrement=True)
#     name = Column(String(50), nullable=False, default="connexion_ok")
#     created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)