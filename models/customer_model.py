from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base_model import Base
from models.associations import customers_contacts_association

class Customer(Base):
    """Représente un client dans la base de données."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    company_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)
    sales_representative_id = Column(Integer, ForeignKey("collaborators.id", name="fk_customers_sales_representative"), nullable=True)
    sales_representative = relationship("Collaborator", back_populates="customers")
    contacts = relationship("Contact", secondary=customers_contacts_association, back_populates="customers")
    contracts = relationship("Contract", back_populates="customer", cascade="all, delete-orphan")

class Contact(Base):
    """Représente un contact associé à un client dans la base de données."""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    customers = relationship("Customer", secondary=customers_contacts_association, back_populates="contacts")
    phone_numbers = relationship("PhoneNumber", back_populates="contact", cascade="all, delete-orphan")

class PhoneNumber(Base):
    """Représente un numéro de téléphone associé à un contact dans la base de données."""
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(String(20), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id", name="fk_phone_number_contact"), nullable=False)
    contact = relationship("Contact", back_populates="phone_numbers")