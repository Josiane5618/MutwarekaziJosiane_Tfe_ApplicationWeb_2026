from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base
from app.models.statuts import StatutCompte

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    prenom = Column(String(100), nullable=False)
    nom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="utilisateur")
    actif = Column(Boolean, default=True)

    @property
    def statut_compte(self) -> str:
        return (
            StatutCompte.ACTIF.value
            if self.actif
            else StatutCompte.EN_ATTENTE.value
        )
