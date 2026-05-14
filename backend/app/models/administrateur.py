from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from app.models.utilisateur import Utilisateur


class Administrateur(Utilisateur):
    """Utilisateur disposant des droits d'administration.

    Implemente par heritage de table unique (single-table inheritance) :
    tous les utilisateurs sont stockes dans la table `utilisateurs`, et la
    colonne `role` sert de discriminant pour distinguer un administrateur
    d'un utilisateur standard.
    """

    niveau_acces = Column(Integer, nullable=True, default=1)
    derniere_action = Column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

    # --- Methodes metier (conformes au diagramme de classes) ---

    def traiter_demandes(self, db: Session) -> List:
        from app.models.demande_inscription import DemandeInscription
        from app.models.statuts import StatutDemandeInscription

        return (
            db.query(DemandeInscription)
            .filter(
                DemandeInscription.statut
                == StatutDemandeInscription.EN_ATTENTE.value
            )
            .all()
        )

    def consulter_tous_logs(self, db: Session) -> List:
        from app.models.log_acces import LogAcces

        return db.query(LogAcces).all()

    def consulter_toutes_reservations(self, db: Session) -> List:
        from app.models.reservation import Reservation

        return db.query(Reservation).all()

    def activer_desactiver_utilisateur(
        self,
        db: Session,
        utilisateur: Utilisateur,
    ) -> bool:
        utilisateur.actif = not utilisateur.actif
        db.commit()
        return utilisateur.actif

    def gerer_salles(self, db: Session, salle) -> bool:
        db.add(salle)
        db.commit()
        return True
