from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from main.base_model import Base


class ContractStatus(PyEnum):
    """Enumeration of possible contract statuses in the EpicEvents CRM.

    Defines the three possible states a contract can be in during its lifecycle.

    :cvar SIGNED: Contract has been signed by all parties and is active.
    :vartype SIGNED: str
    :cvar PENDING: Contract is awaiting signature from one or more parties.
    :vartype PENDING: str
    :cvar CANCELLED: Contract has been cancelled and is no longer active.
    :vartype CANCELLED: str
    """

    SIGNED = "signed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class Contract(Base):
    """Represents a contract in the EpicEvents CRM database.

    Stores financial information, creation date, status, and relationships
    to the associated customer and optional event. Contracts track the
    financial agreement between the company and a customer.

    :cvar id: Unique identifier for the contract, auto-incremented.
    :vartype id: int
    :cvar total_amount: Total monetary value of the contract.
    :vartype total_amount: float
    :cvar amount_due: Remaining balance to be paid on the contract.
        Calculated as total_amount minus payments received.
    :vartype amount_due: float
    :cvar created_at: Date and time when the contract was created (UTC).
        Automatically set to current time on creation.
    :vartype created_at: datetime
    :cvar status: Current status of the contract from ContractStatus enum.
    :vartype status: ContractStatus
    :cvar customer_id: Foreign key reference to the associated customer.
    :vartype customer_id: int
    :cvar customer: Many-to-one relationship with Customer model.
        A customer can have multiple contracts, but each contract belongs
        to exactly one customer.
    :vartype customer: Customer
    :cvar event: One-to-one relationship with Event model.
        A contract can have at most one associated event. Uses cascade
        behavior to delete orphaned events when contract is deleted.
    :vartype event: Event | None

    .. note::
        The event relationship uses cascade="all, delete-orphan" which means
        that if a contract is deleted, its associated event (if it exists) will
        also be automatically deleted to maintain data consistency.
    """

    __tablename__ = "contracts"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    total_amount: float = Column(Float, nullable=False)
    amount_due: float = Column(Float, nullable=False)
    created_at: datetime = Column(
        DateTime, default=datetime.now(UTC), nullable=False
    )
    status: ContractStatus = Column(
        SQLEnum(ContractStatus), nullable=False
    )
    customer_id: int = Column(
        Integer,
        ForeignKey("customers.id", name="fk_contract_customer"),
        nullable=False,
    )
    customer = relationship("Customer", back_populates="contracts")
    event = relationship(
        "Event",
        back_populates="contract",
        uselist=False,
        cascade="all, delete-orphan",
    )
