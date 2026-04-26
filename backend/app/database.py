from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL, SQL_ECHO

engine = create_engine(DATABASE_URL, echo=SQL_ECHO)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
