from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.repositories.users import UserRepository
from app.usecases.auth import AuthUseCase
from app.core import security
from app.core.exceptions import InvalidTokenError, TokenExpiredError
from jose import JWTError, ExpiredSignatureError

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_auth_uc(user_repo: UserRepository = Depends(get_user_repo)) -> AuthUseCase:
    return AuthUseCase(user_repo)

async def get_current_user_id(request: Request) -> int:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise InvalidTokenError()
    token = auth_header.split(" ")[1]
    try:
        payload = security.decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidTokenError()
        return int(user_id)
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()