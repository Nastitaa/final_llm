import pytest
from unittest.mock import AsyncMock, patch
from app.usecases.auth import AuthUseCase
from app.repositories.users import UserRepository
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError
from app.core import security

@pytest.fixture
def mock_user_repo():
    repo = AsyncMock(spec=UserRepository)
    return repo

@pytest.fixture
def auth_uc(mock_user_repo):
    return AuthUseCase(mock_user_repo)

@pytest.mark.asyncio
async def test_register_success(auth_uc, mock_user_repo):
    # Arrange
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = type("User", (), {
        "id": 1,
        "email": "test@example.com",
        "password_hash": "hashed",
        "role": "user",
        "created_at": "2025-01-01"
    })()
    
    # Act
    user = await auth_uc.register("test@example.com", "password123")
    
    # Assert
    mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    mock_user_repo.create.assert_called_once()
    assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_register_user_already_exists(auth_uc, mock_user_repo):
    # Arrange
    mock_user_repo.get_by_email.return_value = object()  # exists
    
    # Act & Assert
    with pytest.raises(UserAlreadyExistsError):
        await auth_uc.register("existing@example.com", "pass")

@pytest.mark.asyncio
async def test_login_success(auth_uc, mock_user_repo):
    # Arrange
    user_mock = AsyncMock()
    user_mock.id = 1
    user_mock.password_hash = security.hash_password("correct_password")
    user_mock.role = "user"
    mock_user_repo.get_by_email.return_value = user_mock
    
    # Act
    token = await auth_uc.login("user@example.com", "correct_password")
    
    # Assert
    assert token is not None
    assert isinstance(token, str)
    # Декодируем токен, чтобы проверить sub
    payload = security.decode_token(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "user"

@pytest.mark.asyncio
async def test_login_invalid_password(auth_uc, mock_user_repo):
    # Arrange
    user_mock = AsyncMock()
    user_mock.password_hash = security.hash_password("correct_password")
    mock_user_repo.get_by_email.return_value = user_mock
    
    # Act & Assert
    with pytest.raises(InvalidCredentialsError):
        await auth_uc.login("user@example.com", "wrong_password")

@pytest.mark.asyncio
async def test_login_user_not_found(auth_uc, mock_user_repo):
    # Arrange
    mock_user_repo.get_by_email.return_value = None
    
    # Act & Assert
    with pytest.raises(InvalidCredentialsError):
        await auth_uc.login("nonexistent@example.com", "pass")

@pytest.mark.asyncio
async def test_me_success(auth_uc, mock_user_repo):
    # Arrange
    user_mock = AsyncMock()
    user_mock.id = 1
    user_mock.email = "me@example.com"
    user_mock.role = "user"
    mock_user_repo.get_by_id.return_value = user_mock
    
    # Act
    user = await auth_uc.me(1)
    
    # Assert
    mock_user_repo.get_by_id.assert_called_once_with(1)
    assert user.id == 1

@pytest.mark.asyncio
async def test_me_user_not_found(auth_uc, mock_user_repo):
    # Arrange
    mock_user_repo.get_by_id.return_value = None
    
    # Act & Assert
    with pytest.raises(UserNotFoundError):
        await auth_uc.me(999)