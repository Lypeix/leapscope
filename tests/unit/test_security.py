from app.core.security import hash_password, verify_password

def test_hash_password_uses_argon2() -> None:
    password = "Finger finger finger finger"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password.startswith("$argon2id$")
    assert verify_password(password, hashed_password)
    assert not verify_password("incorrect password", hashed_password)


def test_hash_password_uses_random_salt() -> None:
    password = "FINGER FINGER FINGER ATTACK TWO"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash