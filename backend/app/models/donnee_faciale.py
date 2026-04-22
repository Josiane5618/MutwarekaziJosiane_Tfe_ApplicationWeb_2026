from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class DonneeFaciale(Base):
    __tablename__ = "donnees_faciales"

    id = Column(Integer, primary_key=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))

    image = Column(LargeBinary, nullable=True)  # ✅ image brute
    encodage = Column(LargeBinary, nullable=False)

    date_enregistrement = Column(DateTime, default=datetime.utcnow)
