from fastapi import HTTPException, status

class BaseHTTPException(HTTPException):
    pass

class UserAlreadyExistsError(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

class InvalidCredentialsError(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

class InvalidTokenError(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

class TokenExpiredError(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

class UserNotFoundError(BaseHTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")