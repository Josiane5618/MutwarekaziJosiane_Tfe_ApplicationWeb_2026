from enum import Enum


class StatutCompte(str, Enum):
    EN_ATTENTE = "EN_ATTENTE"
    ACTIF = "ACTIF"
    REFUSE = "REFUSE"


class StatutReservation(str, Enum):
    CONFIRMEE = "CONFIRMEE"
    ANNULEE = "ANNULEE"


class StatutSalle(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
