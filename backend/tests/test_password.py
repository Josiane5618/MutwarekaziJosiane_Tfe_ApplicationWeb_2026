import pytest

from app.security.password import (
    PasswordTooWeakError,
    hash_password,
    validate_password_strength,
    verify_password,
)


def test_hash_and_verify_password():
    password = "motdepasse123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password) is True
    assert verify_password("mauvais-mot-de-passe", hashed_password) is False


def test_hash_and_verify_long_password():
    password = "a" * 200

    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True


def test_validate_password_strength_accepts_strong_password():
    validate_password_strength("MotDePasse123")


def test_validate_password_strength_rejects_short_password():
    with pytest.raises(PasswordTooWeakError) as exc_info:
        validate_password_strength("Ab1")
    assert "8 caractères" in str(exc_info.value)


def test_validate_password_strength_rejects_password_without_uppercase():
    with pytest.raises(PasswordTooWeakError) as exc_info:
        validate_password_strength("motdepasse123")
    assert "majuscule" in str(exc_info.value)


def test_validate_password_strength_rejects_password_without_lowercase():
    with pytest.raises(PasswordTooWeakError) as exc_info:
        validate_password_strength("MOTDEPASSE123")
    assert "minuscule" in str(exc_info.value)


def test_validate_password_strength_rejects_password_without_digit():
    with pytest.raises(PasswordTooWeakError) as exc_info:
        validate_password_strength("MotDePasseFort")
    assert "chiffre" in str(exc_info.value)
