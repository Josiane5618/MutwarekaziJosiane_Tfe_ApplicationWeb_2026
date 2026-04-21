from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)

    message = Column(String, nullable=False)
    lu = Column(Boolean, default=False)

    date_creation = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship("Utilisateur", backref="notifications")
