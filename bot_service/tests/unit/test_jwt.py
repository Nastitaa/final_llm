from app.core import jwt
from jose import jwt as jose_jwt
from app.core.config import settings

def test_decode_valid():
    token = jose_jwt.encode({"sub": "123"}, settings.jwt_secret, algorithm=settings.jwt_alg)
    payload = jwt.decode_and_validate(token)
    assert payload["sub"] == "123"

def test_decode_invalid():
    import pytest
    with pytest.raises(ValueError):
        jwt.decode_and_validate("invalid")