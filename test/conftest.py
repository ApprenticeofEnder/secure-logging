from urllib.parse import urljoin

import pytest
from httpx import ASGITransport, AsyncClient

from secure_logging.main import CORRECT_PASSWORD, CORRECT_USERNAME, LoginPayload, app


@pytest.fixture
def base_url() -> str:
    return "http://localhost:8000"


@pytest.fixture
def login_url(base_url) -> str:
    return urljoin(base_url, "/login")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def async_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def login_payload() -> LoginPayload:
    return LoginPayload(username=CORRECT_USERNAME, password=CORRECT_PASSWORD)
