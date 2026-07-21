from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from datetime import datetime
from models.base_model import Base
from enum import Enum as PyEnum

class ContractStatus(PyEnum):
    SIGNED = "signed"
    PENDING = "pending"
    CANCELLED = "cancelled"

class Contract(Base):
    """Représente un contrat dans la base de données."""
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    status = Column(SQLEnum(ContractStatus), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer = relationship("Customer", back_populates="contracts")
    event = relationship("Event", back_populates="contract", uselist=False, cascade="all, delete-orphan")