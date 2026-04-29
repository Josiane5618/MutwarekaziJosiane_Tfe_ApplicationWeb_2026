from app.security.password import hash_password, verify_password


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
