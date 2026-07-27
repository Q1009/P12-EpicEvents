from sqlalchemy import Table, Column, Integer, ForeignKey
from models.base_model import Base

# Association tables for Many-to-Many relationships

customers_contacts_association = Table(
    "customers_contacts_association",
    Base.metadata,
    Column("customer_id", Integer, ForeignKey("customers.id"), primary_key=True),
    Column("contact_id", Integer, ForeignKey("contacts.id"), primary_key=True),
)