from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Table
from config.settings import settings

def test_db_connection():
    """Basic test: verifies database connection and access to the Test table."""
    # 1. Create the connection engine
    engine = create_engine(settings.DB_URL)

    # 2. Create a session
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # 3. Insert a test record
        test_entry = Table(name="pytest_connection_ok")
        session.add(test_entry)
        session.commit()

        # 4. Verify that the record was created
        result = session.query(Table).all()

        assert result is not None, "No records found in database"
        assert result[0].name == "pytest_connection_ok", "Name does not match"

        # 5. Clean up (delete the test record)
        for entry in result:
            session.delete(entry)
        session.commit()

        # 6. Verify that the table is empty after deletion
        result_after_delete = session.query(Table).all()
        assert len(result_after_delete) == 0, "Table is not empty"

    # 6. Close the connection
    engine.dispose()