from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from main.base_model import Base


class ContractStatus(PyEnum):
    SIGNED = "signed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class Contract(Base):
    """Represents a contract in the database."""

    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    created_at = Column(
        DateTime, default=datetime.now(UTC), nullable=False
    )
    status = Column(SQLEnum(ContractStatus), nullable=False)
    customer_id = Column(
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
