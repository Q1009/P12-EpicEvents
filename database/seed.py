import random
import subprocess
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bcrypt import hashpw, gensalt
from faker import Faker
from config.settings import settings

# 1. Importe les modèles
from models.base_model import Base
from models.event_model import Event, Location
from models.customer_model import Customer, Contact, PhoneNumber
from models.collaborator_model import Collaborator, Department, DepartmentName
from models.contract_model import Contract, ContractStatus

# 2. Configuration de la session et de Faker (reproductible)
engine = create_engine(settings.DB_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Fixer la graine pour Faker (reproductible)
Faker.seed(42)  # ✅ Même données à chaque exécution
fake = Faker("fr_FR")

# 3. Récupère les mots de passe depuis .env (1 par collaborateur)
# Format attendu dans .env: COLLAB_PASSWORD_1=..., COLLAB_PASSWORD_2=..., etc.
def get_password(index):
    return getattr(settings, f"COLLAB_PASSWORD_{index}", "default_password")

def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt."""
    return hashpw(password.encode(), gensalt()).decode()

# 4. Fonction principale
def seed():
    """Peuple la base de données selon tes spécifications."""

    # ===== Étape 1 : Supprime et recrée les tables (pour un environnement propre)

    subprocess.run(["poetry", "run", "alembic", "downgrade", "base"], check=True, cwd=".")
    subprocess.run(["poetry", "run", "alembic", "upgrade", "head"], check=True, cwd=".")

    # ===== Étape 2 : Crée les départements =====
    departments = [
        Department(name=DepartmentName.SALES.value),
        Department(name=DepartmentName.SUPPORT.value),
        Department(name=DepartmentName.ADMIN.value)
    ]
    session.add_all(departments)
    session.flush()  # Pour obtenir les IDs

    # ===== Étape 3 : Crée les collaborateurs (5 : 3 Sales, 2 Support, 1 Admin) =====
    collaborator_data = [
        {"first_name": "Jean", "last_name": "Dupont", "email": "jean.dupont@epicevents.com", "department": departments[0]},
        {"first_name": "Paul", "last_name": "Martin", "email": "paul.martin@epicevents.com", "department": departments[0]},
        {"first_name": "Marie", "last_name": "Bernard", "email": "marie.bernard@epicevents.com", "department": departments[0]},
        {"first_name": "Sophie", "last_name": "Durand", "email": "sophie.durand@epicevents.com", "department": departments[1]},
        {"first_name": "Pierre", "last_name": "Lefèvre", "email": "pierre.lefevre@epicevents.com", "department": departments[1]},
        {"first_name": "Thomas", "last_name": "Morel", "email": "thomas.morel@epicevents.com", "department": departments[2]}
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

    session.flush()  # Pour obtenir les IDs des collaborateurs

    # Séparation des collaborateurs par département
    sales_collaborators = [c for c in collaborators if c.department.name == DepartmentName.SALES.value]
    support_collaborators = [c for c in collaborators if c.department.name == DepartmentName.SUPPORT.value]

    # ===== Étape 4 : Crée 5 contacts et 5 contacts_customers =====
    contacts = [] # Liste des contacts qui sont les clients
    contacts_customers = [] # Liste des contacts qui sont différents des clients
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

    # ===== Étape 5 : Crée 10 clients avec relations spécifiques =====
    clients = []

    # 5 clients dont le contact est eux-même (le client = le contact)
    for i in range(5):
        client = Customer(
            first_name=contacts[i].first_name,
            last_name=contacts[i].last_name,
            company_name=fake.company(),
            sales_representative=random.choice(sales_collaborators),  # Commercial aléatoire
            contacts=[contacts[i]]  # Le contact est le client lui-même
        )

        clients.append(client)
        session.add(client)

    # 3 clients avec un contact (parmi les 5 contacts_customers)
    for i in range(5, 8):
        client = Customer(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            company_name=fake.company(),
            sales_representative=random.choice(sales_collaborators),
            contacts=[random.choice(contacts_customers)]  # Associe un contact aléatoire
        )

        clients.append(client)
        session.add(client)

    # 2 clients avec 2 contacts chacun
    for i in range(8, 10):
        client = Customer(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            company_name=fake.company(),
            sales_representative=random.choice(sales_collaborators)
        )
        # Sélectionne 2 contacts distincts
        selected_contacts = random.sample(contacts_customers, 2)
        for contact in selected_contacts:
            contact.customers.append(client)
        clients.append(client)
        session.add(client)

    session.flush()

    # ===== Étape 6 : Crée 10 lieux =====
    locations = []
    for _ in range(10):
        location = Location(
            name=fake.location_on_land()[2],  # Nom du lieu basé sur la localisation
            street_number=fake.building_number(),
            street_name=fake.street_name(),
            zip_code=fake.postcode(),
            city=fake.city()
        )
        locations.append(location)
        session.add(location)
    session.flush()

    # ===== Étape 7 : Crée 8 contrats (5 signés, 2 pending, 1 annulé) =====
    contracts = []
    status_distribution = [ContractStatus.SIGNED] * 5 + [ContractStatus.PENDING] * 2 + [ContractStatus.CANCELLED]

    for i, status_enum in enumerate(status_distribution):
        total_amount = round(random.uniform(1000, 50000), 2)
        if status_enum == ContractStatus.SIGNED:
            amount_due = round(random.uniform(0, total_amount), 2)  # Montant dû aléatoire pour les contrats signés
        else:
            amount_due = total_amount  # Montant dû égal au total pour les contrats non signés
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

    # ===== Étape 8 : Crée autant d'événements que de contrats signés et les associe (1:1) =====
    events = []
    signed_contracts = [c for c in contracts if c.status == ContractStatus.SIGNED.value]
    for i, contract in enumerate(signed_contracts):
        # 3 événements avec support, 2 sans
        support_rep = random.choice(support_collaborators) if i < 3 else None

        event = Event(
            name=contract.customer.first_name + " " + contract.customer.last_name + " Event",
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

    # ===== Étape 9 : Crée des numéros de téléphone (1-3 par contact) =====
    for contact in contacts_customers + contacts:
        num_phones = random.randint(1, 3)  # 1, 2 ou 3 numéros par contact
        for _ in range(num_phones):
            phone = PhoneNumber(
                number=fake.phone_number(),
                contact=contact
            )
            session.add(phone)

    # ===== Étape 10 : Finalise =====
    session.commit()
    print("✅ Base de données peuplée avec succès !")
    print(f"   - {len(departments)} départements")
    print(f"   - {len(collaborators)} collaborateurs (3 Sales, 2 Support, 1 Admin)")
    print(f"   - {len(contacts)} contacts")
    print(f"   - {len(clients)} clients")
    print(f"   - {len(locations)} lieux")
    print(f"   - {len(contracts)} contrats (5 signés, 2 pending, 1 annulé)")
    print(f"   - {len(events)} événements")
    print(f"   - {len(session.query(PhoneNumber).all())} numéros de téléphone")

if __name__ == "__main__":
    seed()