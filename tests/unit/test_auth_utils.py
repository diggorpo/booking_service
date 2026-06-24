import pytest
from fastapi import Request, HTTPException
from unittest.mock import MagicMock

from api.api_v1.auth.utils import get_token_from_cookie


@pytest.fixture
def mock_request():
    return MagicMock(spec=Request)


class TestGetTokenFromCookie:
    @pytest.mark.anyio
    async def test_token_present(self, mock_request):
        mock_request.cookies.get.return_value = "test_jwt_token"

        result = await get_token_from_cookie(mock_request)

        assert result == "test_jwt_token"
        mock_request.cookies.get.assert_called_once_with("Authorization")

    @pytest.mark.anyio
    async def test_token_missing(self, mock_request):
        mock_request.cookies.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_token_from_cookie(mock_request)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token is missing"
