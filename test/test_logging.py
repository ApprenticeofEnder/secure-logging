import pytest
import structlog
from fastapi import status
from httpx import AsyncClient
from structlog.testing import LogCapture

from secure_logging.main import LoginPayload

pytestmark = pytest.mark.anyio


@pytest.fixture(name="log_output")
def fixture_log_output() -> LogCapture:
    return LogCapture()


@pytest.fixture(autouse=True)
def fixture_configure_structlog(log_output):
    structlog.configure(processors=[log_output])


async def test_index_logging(async_client: AsyncClient, log_output: LogCapture):
    response = await async_client.get("/")
    assert response.status_code == status.HTTP_200_OK

    event_entry = log_output.entries[0]
    complete_entry = log_output.entries[1]

    test_keys = ["user_agent", "path", "request_id", "log_time"]
    for test_key in test_keys:
        assert event_entry[test_key] == complete_entry[test_key]

    assert event_entry["event"] == "Hello from index!"
    assert complete_entry["event"] == "GET / (200)"

    assert event_entry["security"] == False
    assert complete_entry["security"] == False

    assert complete_entry["status_code"] == status.HTTP_200_OK


async def test_login_logging(
    async_client: AsyncClient, login_payload: LoginPayload, log_output: LogCapture
):
    response = await async_client.post("/login", json=login_payload.model_dump())
    assert response.status_code == status.HTTP_200_OK

    event_entry = log_output.entries[0]
    complete_entry = log_output.entries[1]

    test_keys = ["user_agent", "path", "request_id", "log_time"]
    for test_key in test_keys:
        assert event_entry[test_key] == complete_entry[test_key]

    assert event_entry["event"] == f"User {login_payload.username} has logged in."
    assert complete_entry["event"] == "POST /login (200)"

    assert event_entry["security"] == True
    assert complete_entry["security"] == False

    assert complete_entry["status_code"] == status.HTTP_200_OK


async def test_login_failure(
    async_client: AsyncClient, login_payload: LoginPayload, log_output: LogCapture
):
    login_payload.username = "root"
    response = await async_client.post("/login", json=login_payload.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    event_entry = log_output.entries[0]
    complete_entry = log_output.entries[1]

    assert event_entry["event"] == f"User root has failed to log in."
    assert event_entry["security"] == True

    assert complete_entry["status_code"] == status.HTTP_401_UNAUTHORIZED


async def test_log_injection(
    async_client: AsyncClient, login_payload: LoginPayload, log_output: LogCapture
):
    login_payload.username = "Injection\nTime"
    response = await async_client.post("/login", json=login_payload.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    event_entry = log_output.entries[0]
    complete_entry = log_output.entries[1]

    assert event_entry["event"] == f"User Injection\nTime has failed to log in."
    assert event_entry["security"] == True

    assert complete_entry["status_code"] == status.HTTP_401_UNAUTHORIZED
