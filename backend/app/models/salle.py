from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Salle(Base):
    __tablename__ = "salles"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    capacite = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)

    reservations = relationship("Reservation", back_populates="salle")