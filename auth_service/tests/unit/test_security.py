from app.core import security

def test_hash_password():
    pwd = "secret"
    hashed = security.hash_password(pwd)
    assert hashed != pwd
    assert security.verify_password(pwd, hashed)
    assert not security.verify_password("wrong", hashed)

def test_jwt():
    data = {"sub": "1", "role": "user"}
    token = security.create_access_token(data)
    decoded = security.decode_token(token)
    assert decoded["sub"] == "1"
    assert decoded["role"] == "user"
    assert "exp" in decoded
    assert "iat" in decoded