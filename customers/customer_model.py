from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from customers.associations import customers_contacts_association
from main.base_model import Base


class Customer(Base):
    """Represents a customer in the EpicEvents CRM database.

    Stores information about customers including personal details, company
    information, and relationships to sales representatives, contacts, and contracts.

    :cvar id: Unique identifier for the customer, auto-incremented.
    :vartype id: int
    :cvar first_name: First name of the customer.
    :vartype first_name: str
    :cvar last_name: Last name of the customer.
    :vartype last_name: str
    :cvar company_name: Name of the customer's company or organization.
        Can be null for individual customers.
    :vartype company_name: str | None
    :cvar created_at: Date and time when the customer record was created (UTC).
        Automatically set to current time on creation.
    :vartype created_at: datetime
    :cvar updated_at: Date and time when the customer record was last updated (UTC).
        Automatically set to current time on update.
    :vartype updated_at: datetime
    :cvar sales_representative_id: Foreign key reference to the assigned
        sales representative. Can be null if no representative is assigned.
    :vartype sales_representative_id: int | None
    :cvar sales_representative: Many-to-one relationship with Collaborator model.
        Represents the sales representative assigned to this customer.
    :vartype sales_representative: Collaborator | None
    :cvar contacts: Many-to-many relationship with Contact model.
        A customer can have multiple associated contacts.
    :vartype contacts: list[Contact]
    :cvar contracts: One-to-many relationship with Contract model.
        A customer can have multiple contracts. Uses cascade behavior to
        delete orphaned contracts when customer is deleted.
    :vartype contracts: list[Contract]

    .. note::
        The contracts relationship uses cascade="all, delete-orphan" which means
        that if a customer is deleted, all their associated contracts will also
        be automatically deleted.
    """

    __tablename__ = "customers"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    first_name: str = Column(String(50), nullable=False)
    last_name: str = Column(String(50), nullable=False)
    company_name: str | None = Column(String(100), nullable=True)
    created_at: datetime = Column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: datetime = Column(
        DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    sales_representative_id: int | None = Column(
        Integer,
        ForeignKey(
            "collaborators.id", name="fk_customers_sales_representative"
        ),
        nullable=True,
    )
    sales_representative = relationship(
        "Collaborator", back_populates="customers"
    )
    contacts = relationship(
        "Contact",
        secondary=customers_contacts_association,
        back_populates="customers",
    )
    contracts = relationship(
        "Contract", back_populates="customer", cascade="all, delete-orphan"
    )


class Contact(Base):
    """Represents a contact associated with a customer in the EpicEvents CRM database.

    Stores contact information including name and email, and maintains
    relationships to customers and phone numbers.

    :cvar id: Unique identifier for the contact, auto-incremented.
    :vartype id: int
    :cvar first_name: First name of the contact person.
    :vartype first_name: str
    :cvar last_name: Last name of the contact person.
    :vartype last_name: str
    :cvar email: Email address of the contact. Must be unique across all contacts.
    :vartype email: str
    :cvar customers: Many-to-many relationship with Customer model.
        A contact can be associated with multiple customers.
    :vartype customers: list[Customer]
    :cvar phone_numbers: One-to-many relationship with PhoneNumber model.
        A contact can have multiple phone numbers. Uses cascade behavior to
        delete orphaned phone numbers when contact is deleted.
    :vartype phone_numbers: list[PhoneNumber]

    .. note::
        The email field has a unique constraint to prevent duplicate email
        addresses in the system. The phone_numbers relationship uses
        cascade="all, delete-orphan" to maintain data consistency.
    """

    __tablename__ = "contacts"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    first_name: str = Column(String(50), nullable=False)
    last_name: str = Column(String(50), nullable=False)
    email: str = Column(String(100), nullable=False, unique=True)
    customers = relationship(
        "Customer",
        secondary=customers_contacts_association,
        back_populates="contacts",
    )
    phone_numbers = relationship(
        "PhoneNumber",
        back_populates="contact",
        cascade="all, delete-orphan",
    )


class PhoneNumber(Base):
    """Represents a phone number associated with a contact in the EpicEvents CRM database.

    Stores phone number information and maintains a relationship to the
    associated contact.

    :cvar id: Unique identifier for the phone number, auto-incremented.
    :vartype id: int
    :cvar number: The phone number string, maximum 20 characters.
        Can include country codes, spaces, and special characters.
    :vartype number: str
    :cvar contact_id: Foreign key reference to the associated contact.
    :vartype contact_id: int
    :cvar contact: Many-to-one relationship with Contact model.
        Each phone number belongs to exactly one contact.
    :vartype contact: Contact
    """

    __tablename__ = "phone_numbers"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    number: str = Column(String(20), nullable=False)
    contact_id: int = Column(
        Integer,
        ForeignKey("contacts.id", name="fk_phone_number_contact"),
        nullable=False,
    )
    contact = relationship("Contact", back_populates="phone_numbers")
