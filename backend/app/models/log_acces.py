from datetime import datetime, timedelta
from typing import List

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Session, relationship

from app.database import Base
from app.models.statuts import ResultatVerification


class LogAcces(Base):
    __tablename__ = "logs_acces"

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)

    horodatage = Column("date_acces", DateTime, default=datetime.utcnow)
    resultat = Column(String, nullable=False)
    score_confiance = Column("distance", Float, nullable=True)
    details = Column(String, nullable=True)

    utilisateur = relationship("Utilisateur", backref="logs_acces")

    # --- Methodes metier (conformes au diagramme de classes) ---

    def enregistrer(self, db: Session) -> bool:
        db.add(self)
        db.commit()
        return True

    @classmethod
    def get_logs_par_utilisateur(
        cls,
        db: Session,
        utilisateur_id: int,
    ) -> List:
        return (
            db.query(cls)
            .filter(cls.utilisateur_id == utilisateur_id)
            .all()
        )

    @classmethod
    def get_taux_echecs(cls, db: Session, periode: str) -> float:
        maintenant = datetime.utcnow()
        if periode == "jour":
            depuis = maintenant - timedelta(days=1)
        elif periode == "semaine":
            depuis = maintenant - timedelta(days=7)
        else:
            depuis = maintenant - timedelta(days=30)

        logs = db.query(cls).filter(cls.horodatage >= depuis).all()
        total = len(logs)
        if total == 0:
            return 0.0

        echecs = sum(
            1
            for log in logs
            if log.resultat == ResultatVerification.ACCES_REFUSE.value
        )
        return (echecs / total) * 100.0
