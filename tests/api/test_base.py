import pytest
from fastapi import status
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


async def test_liveness_probe(client: AsyncClient):
    response = await client.get("/livez")

    assert response.status_code == status.HTTP_200_OK
    assert response.text == '"OK"'


async def test_readiness_probe(client: AsyncClient):
    response = await client.get("/healthz")

    assert response.status_code == status.HTTP_200_OK
    assert response.text == '"OK"'


async def test_error_handling(client: AsyncClient):
    response = await client.get("/http_error")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"details": None, "error": True, "message": ""}
