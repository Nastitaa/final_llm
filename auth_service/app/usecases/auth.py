from app.repositories.users import UserRepository
from app.core import security
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError

class AuthUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, email: str, password: str):
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError()
        hashed = security.hash_password(password)
        user = await self.user_repo.create(email, hashed)
        return user

    async def login(self, email: str, password: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if not user or not security.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        token_data = {"sub": str(user.id), "role": user.role}
        return security.create_access_token(token_data)

    async def me(self, user_id: int):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user