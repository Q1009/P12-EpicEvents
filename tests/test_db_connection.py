# tests/test_db_connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Table
from config.settings import settings

def test_db_connection():
    """Test basique : vérifie la connexion à la BDD et l'accès à la table Test."""
    # 1. Crée le moteur de connexion
    engine = create_engine(settings.DB_URL)

    # 2. Crée une session
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # 3. Insère un enregistrement de test
        test_entry = Table(name="pytest_connection_ok")
        session.add(test_entry)
        session.commit()

        # 4. Vérifie que l'enregistrement a été créé
        result = session.query(Table).all()

        assert result is not None, "Aucun enregistrement trouvé en BDD"
        assert result[0].name == "pytest_connection_ok", "Le nom ne correspond pas"

        # 5. Nettoie (supprime l'enregistrement de test)
        for entry in result:
            session.delete(entry)
        session.commit()

        # 6. Vérifie que la table est vide après suppression
        result_after_delete = session.query(Table).all()
        assert len(result_after_delete) == 0, "La table n'est pas vide"

    # 6. Ferme la connexion
    engine.dispose()