from pathlib import Path
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base  # noqa: E402
from app.models.donnee_faciale import DonneeFaciale  # noqa: F401, E402
from app.models.log_acces import LogAcces  # noqa: F401, E402
from app.models.notification import Notification  # noqa: F401, E402
from app.models.reservation import Reservation  # noqa: F401, E402
from app.models.salle import Salle  # noqa: F401, E402
from app.models.utilisateur import Utilisateur  # noqa: F401, E402


@pytest.fixture
def db_session(tmp_path):
    database_path = tmp_path / "test_backend.sqlite3"
    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
