import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Collaborator
from config.settings import settings

@pytest.fixture(scope="module")  # Shared across all tests in this module
def db_session():
    """
    Fixture that provides a database session for the entire test module.
    - Creates session before first test
    - Destroys session after last test
    - Shared across all tests in this file
    """

    engine = create_engine(settings.DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session  # Tests run here

    # Cleanup (runs after all tests in the module)
    session.close()
    engine.dispose()


class TestCollaboratorQueries:
    """Test suite for collaborator queries."""

    def test_get_all_collaborators(self, db_session):
        """Test that retrieves all collaborators from the collaborators table in DB"""
        collaborators = db_session.query(Collaborator).all()

        assert collaborators is not None
        assert len(collaborators) > 0
        assert all(isinstance(c, Collaborator) for c in collaborators)

    def test_get_first_collaborator(self, db_session):
        """Test that gets the first collaborator"""

        collaborator = db_session.query(Collaborator).first()

        assert collaborator is not None
        assert collaborator.first_name == "Jean"
        assert collaborator.last_name == "Dupont"

    def test_get_collaborator_by_attribute(self, db_session):
        """Test that retrieves a collaborator by a specific attribute (e.g., email, first_name, last_name)"""

        # Query a collaborator by email (using known data from seed.py)
        collaborator_by_email = db_session.query(Collaborator).filter_by(
            email="jean.dupont@epicevents.com"
        ).first()

        assert collaborator_by_email is not None, "Collaborator with email 'jean.dupont@epicevents.com' not found"
        assert collaborator_by_email.email == "jean.dupont@epicevents.com"
        assert collaborator_by_email.first_name == "Jean"
        assert collaborator_by_email.last_name == "Dupont"

        # Query a collaborator by first_name
        collaborator_by_first_name = db_session.query(Collaborator).filter_by(
            first_name="Paul"
        ).first()

        assert collaborator_by_first_name is not None, "Collaborator with first_name 'Paul' not found"
        assert collaborator_by_first_name.first_name == "Paul"
        assert collaborator_by_first_name.last_name == "Martin"

        # Query a collaborator by last_name
        collaborator_by_last_name = db_session.query(Collaborator).filter_by(
            last_name="Bernard"
        ).first()

        assert collaborator_by_last_name is not None, "Collaborator with last_name 'Bernard' not found"
        assert collaborator_by_last_name.last_name == "Bernard"
        assert collaborator_by_last_name.first_name == "Marie"

        # Query a collaborator by department name
        collaborator_by_department = db_session.query(Collaborator).filter_by(
            department_id=3
        ).first()

        assert collaborator_by_department is not None
        assert collaborator_by_department.first_name == "Thomas"