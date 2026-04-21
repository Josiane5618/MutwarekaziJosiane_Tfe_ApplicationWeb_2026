from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class LogAcces(Base):
    __tablename__ = "logs_acces"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)

    date_acces = Column(DateTime, default=datetime.utcnow)

    resultat = Column(String, nullable=False)  # ACCES_AUTORISE / ACCES_REFUSE
    distance = Column(Float, nullable=True)

    utilisateur = relationship("Utilisateur", backref="logs_acces")