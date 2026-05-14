from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from app.database import Base
from app.models.statuts import StatutDemandeInscription, TypeNotification


class DemandeInscription(Base):
    __tablename__ = "demandes_inscription"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(
        Integer,
        ForeignKey("utilisateurs.id"),
        nullable=False,
    )
    date_soumission = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_traitement = Column(DateTime, nullable=True)
    commentaire_refus = Column(String, nullable=True)
    statut = Column(
        String(50),
        nullable=False,
        default=StatutDemandeInscription.EN_ATTENTE.value,
    )

    utilisateur = relationship(
        "Utilisateur",
        back_populates="demandes_inscription",
    )

    # --- Methodes metier (conformes au diagramme de classes) ---

    def accepter(self) -> bool:
        if self.est_traitee():
            return False
        self.statut = StatutDemandeInscription.ACCEPTEE.value
        self.date_traitement = datetime.utcnow()
        if self.utilisateur is not None:
            self.utilisateur.actif = True
        return True

    def refuser(self, commentaire: Optional[str] = None) -> bool:
        if self.est_traitee():
            return False
        self.statut = StatutDemandeInscription.REFUSEE.value
        self.date_traitement = datetime.utcnow()
        self.commentaire_refus = commentaire
        if self.utilisateur is not None:
            self.utilisateur.actif = False
        return True

    def est_traitee(self) -> bool:
        return self.statut != StatutDemandeInscription.EN_ATTENTE.value

    def notifier(self, db: Session) -> bool:
        from app.models.notification import Notification

        if self.utilisateur is None:
            return False

        if self.statut == StatutDemandeInscription.ACCEPTEE.value:
            type_notif = TypeNotification.ACCEPTATION_INSCRIPTION.value
            sujet = "Inscription acceptee"
            message = "Votre demande d'inscription a ete acceptee."
        elif self.statut == StatutDemandeInscription.REFUSEE.value:
            type_notif = TypeNotification.REFUS_INSCRIPTION.value
            sujet = "Inscription refusee"
            message = "Votre demande d'inscription a ete refusee."
        else:
            return False

        notif = Notification(
            utilisateur_id=self.utilisateur.id,
            sujet=sujet,
            message=message,
            type=type_notif,
        )
        db.add(notif)
        return True
