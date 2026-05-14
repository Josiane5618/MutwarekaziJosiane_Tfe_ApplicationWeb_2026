from datetime import datetime
from typing import Any

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)

    sujet = Column(String, nullable=True)
    message = Column(String, nullable=False)
    type = Column(String(50), nullable=True)
    lu = Column(Boolean, default=False)
    est_envoyee = Column(Boolean, nullable=False, default=True)

    date_envoi = Column("date_creation", DateTime, default=datetime.utcnow)

    utilisateur = relationship("Utilisateur", backref="notifications")

    # --- Methodes metier (conformes au diagramme de classes) ---

    def envoyer(self) -> bool:
        from app.utils.email_service import send_email

        if self.utilisateur is None:
            self.est_envoyee = False
            return False

        envoye = send_email(
            self.utilisateur.email,
            self.sujet or "Notification",
            self.message,
        )
        self.est_envoyee = bool(envoye)
        return self.est_envoyee

    def generer_message(self) -> str:
        return self.message or ""

    def reessayer(self) -> bool:
        self.est_envoyee = False
        return self.envoyer()

    def get_attribute(self, attribute: str) -> Any:
        return getattr(self, attribute, None)

    def set_attribute(self, attribute: str, value: Any) -> None:
        setattr(self, attribute, value)
