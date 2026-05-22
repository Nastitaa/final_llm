from jose import jwt, ExpiredSignatureError, JWTError
from app.core.config import settings

def decode_and_validate(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
        if not payload.get("sub"):
            raise ValueError("Missing sub")
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token expired")
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")