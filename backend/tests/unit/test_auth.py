from app.auth import create_access_token, decode_token, hash_password, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_create_and_decode_token():
    token = create_access_token(user_id=1, username="admin")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["username"] == "admin"
    assert "exp" in payload


def test_decode_invalid_token():
    assert decode_token("invalid.token.here") is None
