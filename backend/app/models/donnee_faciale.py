from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary
from sqlalchemy.orm import relationship

from app.database import Base


class DonneeFaciale(Base):
    __tablename__ = "donnees_faciales"

    id = Column(Integer, primary_key=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"))

    image_path = Column("image", LargeBinary, nullable=True)
    encodage_facial = Column("encodage", LargeBinary, nullable=False)
    est_chiffre = Column(Boolean, nullable=False, default=False)
    date_enregistrement = Column(DateTime, default=datetime.utcnow)

    utilisateur = relationship(
        "Utilisateur",
        back_populates="donnees_faciales",
    )

    # --- Methodes metier (conformes au diagramme de classes) ---

    def comparer(self, encodage: bytes) -> float:
        import numpy as np

        from app.security.biometric_cipher import decrypt_encoding

        reference_brut = (
            decrypt_encoding(self.encodage_facial)
            if self.est_chiffre
            else self.encodage_facial
        )
        reference = np.frombuffer(reference_brut, dtype=np.float32)
        autre = np.frombuffer(encodage, dtype=np.float32)
        return float(np.linalg.norm(reference - autre))

    def chiffrer(self) -> bytes:
        from app.security.biometric_cipher import encrypt_encoding

        if not self.est_chiffre:
            self.encodage_facial = encrypt_encoding(self.encodage_facial)
            self.est_chiffre = True
        return self.encodage_facial

    def dechiffrer(self) -> bytes:
        from app.security.biometric_cipher import decrypt_encoding

        if self.est_chiffre:
            return decrypt_encoding(self.encodage_facial)
        return self.encodage_facial
