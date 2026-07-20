from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base
from enum import Enum as PyEnum

class Role(PyEnum):
    ADMIN = "admin"
    SALES = "sales"
    SUPPORT = "support"

class Collaborator(Base):
    __tablename__ = "collaborators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # À hasher avec bcrypt
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    department = relationship("Department", back_populates="collaborators")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(SQLEnum(Role), nullable=False)
    collaborators = relationship("Collaborator", back_populates="department")