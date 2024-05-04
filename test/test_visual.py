import asyncio

import pytest
import requests

from secure_logging.main import LoginPayload

pytestmark = pytest.mark.anyio


async def test_index(base_url):
    response = await asyncio.to_thread(requests.get, base_url)
    assert response.status_code == 200


async def test_login_success(login_url, login_payload: LoginPayload):
    response = await asyncio.to_thread(
        requests.post, login_url, json=login_payload.model_dump()
    )
    assert response.status_code == 200


async def test_login_failure(login_url, login_payload: LoginPayload):
    login_payload.username = "root"
    response = await asyncio.to_thread(
        requests.post, login_url, json=login_payload.model_dump()
    )
    assert response.status_code == 401


async def test_login_injection(login_url, login_payload: LoginPayload):
    login_payload.username = "Injection\nTime"
    response = await asyncio.to_thread(
        requests.post, login_url, json=login_payload.model_dump()
    )
    assert response.status_code == 401
