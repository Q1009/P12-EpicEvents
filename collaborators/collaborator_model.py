from enum import Enum as PyEnum

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from main.base_model import Base


class DepartmentName(PyEnum):
    """Enumeration of possible department names in the EpicEvents CRM.

    Defines the three organizational departments in the company.

    :cvar ADMIN: Administration department responsible for system management
        and user permissions.
    :vartype ADMIN: str
    :cvar SALES: Sales department responsible for customer relationships
        and contract management.
    :vartype SALES: str
    :cvar SUPPORT: Support department responsible for event management
        and customer assistance.
    :vartype SUPPORT: str
    """

    ADMIN = "admin"
    SALES = "sales"
    SUPPORT = "support"


class Collaborator(Base):
    """Represents a collaborator (employee) in the EpicEvents CRM database.

    Stores employee information including personal details, credentials,
    department assignment, and relationships to customers and events.

    :cvar id: Unique identifier for the collaborator, auto-incremented.
    :vartype id: int
    :cvar first_name: First name of the collaborator.
    :vartype first_name: str
    :cvar last_name: Last name of the collaborator.
    :vartype last_name: str
    :cvar email: Email address of the collaborator. Must be unique.
    :vartype email: str
    :cvar password: Hashed password for authentication.
    :vartype password: str
    :cvar department_id: Foreign key reference to the collaborator's department.
    :vartype department_id: int
    :cvar department: Many-to-one relationship with Department model.
        Each collaborator belongs to exactly one department.
    :vartype department: Department
    :cvar customers: One-to-many relationship with Customer model.
        Collaborators in the SALES department can be assigned as sales
        representatives for multiple customers.
    :vartype customers: list[Customer]
    :cvar events: One-to-many relationship with Event model.
        Collaborators in the SUPPORT department can be assigned as support
        representatives for multiple events.
    :vartype events: list[Event]
    """

    __tablename__ = "collaborators"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    first_name: str = Column(String(50), nullable=False)
    last_name: str = Column(String(50), nullable=False)
    email: str = Column(String(100), unique=True, nullable=False)
    password: str = Column(String(100), nullable=False)
    department_id: int = Column(
        Integer,
        ForeignKey("departments.id", name="fk_collaborator_department"),
        nullable=False,
    )
    department = relationship("Department", back_populates="collaborators")
    customers = relationship(
        "Customer", back_populates="sales_representative"
    )
    events = relationship("Event", back_populates="support_representative")


class Department(Base):
    """Represents a department in the EpicEvents CRM database.

    Stores department information including name and relationships to
    collaborators working in that department.

    :cvar id: Unique identifier for the department, auto-incremented.
    :vartype id: int
    :cvar name: Name of the department from DepartmentName enum.
    :vartype name: DepartmentName
    :cvar collaborators: One-to-many relationship with Collaborator model.
        A department can have multiple collaborators.
    :vartype collaborators: list[Collaborator]
    """

    __tablename__ = "departments"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: DepartmentName = Column(SQLEnum(DepartmentName), nullable=False)
    collaborators = relationship(
        "Collaborator", back_populates="department"
    )
