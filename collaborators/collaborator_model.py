from enum import Enum as PyEnum

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from main.base_model import Base


class DepartmentName(PyEnum):
    ADMIN = "admin"
    SALES = "sales"
    SUPPORT = "support"


class Collaborator(Base):
    __tablename__ = "collaborators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    department_id = Column(
        Integer,
        ForeignKey("departments.id", name="fk_collaborator_department"),
        nullable=False,
    )
    department = relationship("Department", back_populates="collaborators")
    customers = relationship("Customer", back_populates="sales_representative")
    events = relationship("Event", back_populates="support_representative")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(SQLEnum(DepartmentName), nullable=False)
    collaborators = relationship("Collaborator", back_populates="department")
