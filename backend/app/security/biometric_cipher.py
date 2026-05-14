"""Chiffrement symetrique des donnees biometriques.

L'encodage facial (vecteur de 128 floats) est une donnee biometrique sensible.
Pour respecter l'exigence de protection des donnees biometriques mentionnee
dans le cahier des charges, on chiffre ce vecteur en base avec Fernet
(AES-128 en mode CBC + HMAC-SHA256, fourni par la librairie cryptography).
"""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.config import BIOMETRIC_ENCRYPTION_KEY


def _derive_fernet_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


_fernet = Fernet(_derive_fernet_key(BIOMETRIC_ENCRYPTION_KEY))


def encrypt_encoding(plaintext: bytes) -> bytes:
    return _fernet.encrypt(plaintext)


def decrypt_encoding(ciphertext: bytes) -> bytes:
    try:
        return _fernet.decrypt(ciphertext)
    except InvalidToken as exc:
        raise ValueError("Encodage biometrique impossible a dechiffrer") from exc
