# == Command to run seed.py ==
# poetry run python -m database.seed

import random
import subprocess
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bcrypt import hashpw, gensalt
from faker import Faker
from config.settings import settings

# 1. Import models
from main.base_model import Base
from events.event_model import Event, Location
from customers.customer_model import Customer, Contact, PhoneNumber
from collaborators.collaborator_model import Collaborator, Department, DepartmentName
from contracts.contract_model import Contract, ContractStatus

# 2. Session and Faker configuration
engine = create_engine(settings.DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Faker seed for reproducibility
Faker.seed(42)
fake = Faker("fr_FR")

# 3. Get passwords from .env (1 per collaborator) and hash them using bcrypt
# Expected format in .env: COLLAB_PASSWORD_1=..., COLLAB_PASSWORD_2=..., etc.


def get_password(index):
    return getattr(settings, f"COLLAB_PASSWORD_{index}", "default_password")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt and return the hashed password as a string."""
    return hashpw(password.encode(), gensalt()).decode()

# 4. Main seeding function


def seed():
    """Seed the database with initial data."""

    # ===== Step 1 : Drop and recreate the database schema =====

    subprocess.run(["poetry", "run", "alembic", "downgrade",
                   "base"], check=True, cwd=".")
    subprocess.run(["poetry", "run", "alembic", "upgrade",
                   "head"], check=True, cwd=".")

    # ===== Step 2 : Create departments =====
    departments = [
        Department(name=DepartmentName.SALES.value),
        Department(name=DepartmentName.SUPPORT.value),
        Department(name=DepartmentName.ADMIN.value)
    ]
    session.add_all(departments)
    session.flush()  # To get IDs for departments

    # ===== Step 3 : Create collaborators (5 : 3 Sales, 2 Support, 1 Admin) =====
    collaborator_data = [
        {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@epicevents.com",
            "department": departments[0]
        },
        {
            "first_name": "Paul",
            "last_name": "Martin",
            "email": "paul.martin@epicevents.com",
            "department": departments[0]
        },
        {
            "first_name": "Marie",
            "last_name": "Bernard",
            "email": "marie.bernard@epicevents.com",
            "department": departments[0]
        },
        {
            "first_name": "Sophie",
            "last_name": "Durand",
            "email": "sophie.durand@epicevents.com",
            "department": departments[1]
        },
        {
            "first_name": "Pierre",
            "last_name": "Lefèvre",
            "email": "pierre.lefevre@epicevents.com",
            "department": departments[1]
        },
        {
            "first_name": "Thomas",
            "last_name": "Morel",
            "email": "thomas.morel@epicevents.com",
            "department": departments[2]
        }
    ]

    collaborators = []
    for i, data in enumerate(collaborator_data, start=1):
        collab = Collaborator(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=hash_password(get_password(i)),
            department=data["department"]
        )
        collaborators.append(collab)
        session.add(collab)

    session.flush()  # To get IDs for collaborators

    # Segregate collaborators by department for later use
    sales_collaborators = [
        c for c in collaborators if c.department.name == DepartmentName.SALES.value]
    support_collaborators = [
        c for c in collaborators if c.department.name == DepartmentName.SUPPORT.value]

    # ===== Step 4 : Create 5 contacts and 5 contacts_customers =====
    contacts = []  # List of contacts who are the clients
    contacts_customers = []  # List of contacts who are different from the clients
    for _ in range(5):
        contact = Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email()
        )

        contact_customer = Contact(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email()
        )

        contacts.append(contact)
        contacts_customers.append(contact_customer)
        session.add(contact, contact_customer)

    session.flush()

    # ===== Step 5 : Create 10 clients with specific relationships =====
    clients = []

    # 5 clients whose contact is themselves (the client = the contact)
    for i in range(5):
        client = Customer(
            first_name=contacts[i].first_name,
            last_name=contacts[i].last_name,
            company_name=fake.company(),
            # Randomly assign a sales representative
            sales_representative=random.choice(sales_collaborators),
            contacts=[contacts[i]]  # The contact is the client himself
        )

        clients.append(client)
        session.add(client)

    # 3 clients with a unique contact (among the 5 contacts_customers)
    for i in range(5, 8):
        client = Customer(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            company_name=fake.company(),
            sales_representative=random.choice(sales_collaborators),
            # Randomly assign one of the contacts_customers as the contact
            contacts=[random.choice(contacts_customers)]
        )

        clients.append(client)
        session.add(client)

    # 2 clients with 2 contacts each
    for i in range(8, 10):
        client = Customer(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            company_name=fake.company(),
            sales_representative=random.choice(sales_collaborators)
        )
        # Select 2 distinct contacts from contacts_customers
        selected_contacts = random.sample(contacts_customers, 2)
        for contact in selected_contacts:
            contact.customers.append(client)
        clients.append(client)
        session.add(client)

    session.flush()

    # ===== Step 6 : Create 10 locations =====
    locations = []
    for _ in range(10):
        location = Location(
            # Name of the location based on the location
            name=fake.location_on_land()[2],
            street_number=fake.building_number(),
            street_name=fake.street_name(),
            zip_code=fake.postcode(),
            city=fake.city()
        )
        locations.append(location)
        session.add(location)
    session.flush()

    # ===== Step 7 : Create 8 contracts (5 signed, 2 pending, 1 cancelled) =====
    contracts = []
    status_distribution = [ContractStatus.SIGNED] * 5 + \
        [ContractStatus.PENDING] * 2 + [ContractStatus.CANCELLED]

    for i, status_enum in enumerate(status_distribution):
        total_amount = round(random.uniform(1000, 50000), 2)
        if status_enum == ContractStatus.SIGNED:
            # Random amount due for signed contracts
            amount_due = round(random.uniform(0, total_amount), 2)
        else:
            amount_due = total_amount  # Amount due equal to total for unsigned contracts
        contract = Contract(
            total_amount=total_amount,
            amount_due=amount_due,
            created_at=fake.date_between(start_date='-1y', end_date='today'),
            status=status_enum.value,
            customer=random.choice(clients)
        )
        contracts.append(contract)
        session.add(contract)
    session.flush()

    # ===== Step 8 : Create as many events as there are signed contracts and associate them (1:1) =====
    events = []
    signed_contracts = [c for c in contracts if c.status ==
                        ContractStatus.SIGNED.value]
    for i, contract in enumerate(signed_contracts):
        # 3 events with support, 2 without
        support_rep = random.choice(support_collaborators) if i < 3 else None

        event = Event(
            name=contract.customer.first_name + " " +
            contract.customer.last_name + " Event",
            start_date=fake.date_between(start_date='today', end_date='+6M'),
            end_date=fake.date_between(start_date='+1d', end_date='+6M'),
            attendees=fake.random_number(digits=3, fix_len=False),
            description=fake.text(max_nb_chars=1000),
            location=random.choice(locations),
            support_representative=support_rep,
            contract=contract
        )
        events.append(event)
        session.add(event)

    # ===== Step 9 : Create phone numbers (1-3 per contact) =====
    for contact in contacts_customers + contacts:
        num_phones = random.randint(1, 3)  # 1, 2 or 3 numbers per contact
        for _ in range(num_phones):
            phone = PhoneNumber(
                number=fake.phone_number(),
                contact=contact
            )
            session.add(phone)

    # ===== Step 10 : Finalize =====
    session.commit()
    print("✅ Database seeded successfully with the following data:")
    print(f"   - {len(departments)} departments")
    print(
        f"   - {len(collaborators)} collaborators (3 Sales, 2 Support, 1 Admin)")
    print(f"   - {len(contacts)+len(contacts_customers)} contacts")
    print(f"   - {len(clients)} customers (5 with self-contact, 3 with unique contact, 2 with 2 contacts each)")
    print(f"   - {len(locations)} locations")
    print(f"   - {len(contracts)} contracts (5 signed, 2 pending, 1 cancelled)")
    print(f"   - {len(events)} events (3 with support, 2 without support)")
    print(f"   - {len(session.query(PhoneNumber).all())} phone numbers")
