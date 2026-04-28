from enum import Enum


class StatutCompte(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    ACTIF = "ACTIF"
    REFUSE = "REFUSE"


class StatutDemandeInscription(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    ACCEPTEE = "ACCEPTEE"
    REFUSEE = "REFUSEE"


class StatutReservation(str, Enum):
    CONFIRMEE = "CONFIRMEE"
    ANNULEE = "ANNULEE"


class StatutSalle(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
