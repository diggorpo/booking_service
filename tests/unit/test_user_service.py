from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from api.api_v1.auth.service import UserService
from api.api_v1.auth.schemas import RegisterUserSchema, UserResponseSchema, PhoneNumber
from api.api_v1.auth.handler import AuthHandler
from core.infrastructure.db.repositories.users import UserRepository


@pytest.fixture
def mock_db_session():
    return AsyncMock()


@pytest.fixture
def mock_user_repo():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_auth_handler():
    handler = AsyncMock(spec=AuthHandler)
    handler.hash_password = MagicMock(return_value=b"hashed_password")
    handler.validate_password = AsyncMock(return_value=True)
    return handler


@pytest.fixture
def user_service(mock_db_session, mock_user_repo, mock_auth_handler):
    service = UserService.__new__(UserService)
    service.db_session = mock_db_session
    service.user_repo = mock_user_repo
    service.auth_handler = mock_auth_handler
    return service


@pytest.fixture
def valid_register_user():
    return RegisterUserSchema(
        first_name="Yaroslav",
        last_name="Nikolaev",
        email="yaroslav@example.com",
        phone_number=PhoneNumber("+79991112233"),
        password="securepassword123",
    )


@pytest.fixture
def mock_created_user():
    mock = MagicMock()
    mock.id = 1
    mock.first_name = "Yaroslav"
    mock.last_name = "Nikolaev"
    mock.email = "yaroslav@example.com"
    mock.phone_number = PhoneNumber("+79991112233")
    mock.role = MagicMock()
    mock.role.id = 3
    mock.role.name = "client"
    return mock


class TestRegisterUser:
    @pytest.mark.anyio
    async def test_register_user_success(
        self,
        user_service,
        mock_user_repo,
        mock_db_session,
        valid_register_user,
        mock_created_user,
    ):
        mock_user_repo.create.return_value = mock_created_user

        result = await user_service.register_user(valid_register_user)

        assert isinstance(result, UserResponseSchema)
        assert result.id == 1
        assert result.email == "yaroslav@example.com"
        assert result.first_name == "Yaroslav"
        assert result.last_name == "Nikolaev"
        mock_user_repo.create.assert_awaited_once()
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.anyio
    async def test_register_user_duplicate_email(
        self, user_service, mock_user_repo, mock_db_session, valid_register_user
    ):
        mock_user_repo.create.side_effect = IntegrityError("", "", Exception(""))

        with pytest.raises(HTTPException) as exc_info:
            await user_service.register_user(valid_register_user)

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "User with such email already exists"
        mock_user_repo.create.assert_awaited_once()
        mock_db_session.commit.assert_not_awaited()

    @pytest.mark.anyio
    async def test_register_user_password_hashing(
        self, user_service, mock_auth_handler, mock_user_repo, valid_register_user
    ):
        mock_user_repo.create.side_effect = IntegrityError("", "", Exception(""))

        with pytest.raises(HTTPException):
            await user_service.register_user(valid_register_user)

        mock_auth_handler.hash_password.assert_called_once_with(
            valid_register_user.password
        )


class TestLoginUser:
    @pytest.mark.anyio
    async def test_login_success(self, user_service, mock_user_repo, mock_auth_handler):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "client@example.com"
        mock_user.password_hash = b"hashed_password"
        mock_user_repo.find_one.return_value = mock_user

        mock_auth_handler.encode_jwt.return_value = ("jwt_token", "session_id_123")

        result = await user_service.login_user("client@example.com", "password123")

        assert result is not None
        assert "Login successful" in str(result.body)
        mock_user_repo.find_one.assert_awaited_once_with(email="client@example.com")
        mock_auth_handler.validate_password.assert_awaited_once_with(
            "password123", b"hashed_password"
        )
        mock_auth_handler.encode_jwt.assert_awaited_once_with({"user_id": 1})

    @pytest.mark.anyio
    async def test_login_user_not_found(self, user_service, mock_user_repo):
        mock_user_repo.find_one.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await user_service.login_user("nonexistent@example.com", "password123")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid email or password"

    @pytest.mark.anyio
    async def test_login_invalid_password(
        self, user_service, mock_user_repo, mock_auth_handler
    ):
        mock_user = MagicMock()
        mock_user.password_hash = b"hashed_password"
        mock_user_repo.find_one.return_value = mock_user

        mock_auth_handler.validate_password.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await user_service.login_user("client@example.com", "wrongpassword")

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid email or password"


class TestGetUserById:
    @pytest.mark.anyio
    async def test_get_user_by_id_success(
        self, user_service, mock_user_repo, mock_created_user
    ):
        mock_user_repo.get_by_id.return_value = mock_created_user

        result = await user_service.get_user_by_id(1)

        assert isinstance(result, UserResponseSchema)
        assert result.id == 1
        assert result.email == "yaroslav@example.com"
        mock_user_repo.get_by_id.assert_awaited_once_with(1, ["role"])

    @pytest.mark.anyio
    async def test_get_user_by_id_not_found(self, user_service, mock_user_repo):
        mock_user_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await user_service.get_user_by_id(999)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "User not found"


class TestLogoutUser:
    @pytest.mark.anyio
    async def test_logout_user(self, user_service):
        mock_user = MagicMock()
        mock_user.id = 1

        result = await user_service.logout_user(mock_user)

        assert result is not None
        assert "Logged out" in str(result.body)
