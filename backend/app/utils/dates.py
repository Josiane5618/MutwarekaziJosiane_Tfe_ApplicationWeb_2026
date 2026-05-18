from datetime import datetime, timezone
from typing import Optional


def to_iso_utc(valeur: Optional[datetime]) -> Optional[str]:
    """Sérialise une date/heure stockée en UTC (naïve ou non) au format ISO 8601
    avec marqueur de fuseau, afin que les clients la convertissent correctement
    en heure locale (l'application stocke tous les horodatages en UTC)."""

    if valeur is None:
        return None

    if valeur.tzinfo is None:
        valeur = valeur.replace(tzinfo=timezone.utc)
    else:
        valeur = valeur.astimezone(timezone.utc)

    return valeur.isoformat().replace("+00:00", "Z")
