import bcrypt
import hashlib
import re


class PasswordTooWeakError(ValueError):
    """Erreur levee quand un mot de passe ne respecte pas les exigences."""


def _normalize_password(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8")


def hash_password(password: str) -> str:
    password_bytes = _normalize_password(password)
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    password_bytes = _normalize_password(password)
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)


def validate_password_strength(password: str) -> None:
    """Verifie qu'un mot de passe respecte les exigences minimales.

    Exigences :
    - au moins 8 caracteres
    - au moins une lettre majuscule
    - au moins une lettre minuscule
    - au moins un chiffre

    Leve PasswordTooWeakError si une exigence n'est pas respectee.
    """
    if len(password) < 8:
        raise PasswordTooWeakError(
            "Le mot de passe doit contenir au moins 8 caractères."
        )

    if not re.search(r"[A-Z]", password):
        raise PasswordTooWeakError(
            "Le mot de passe doit contenir au moins une lettre majuscule."
        )

    if not re.search(r"[a-z]", password):
        raise PasswordTooWeakError(
            "Le mot de passe doit contenir au moins une lettre minuscule."
        )

    if not re.search(r"\d", password):
        raise PasswordTooWeakError(
            "Le mot de passe doit contenir au moins un chiffre."
        )
