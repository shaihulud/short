import pytest
from fastapi import status
from httpx import AsyncClient

from app.apps.urls import models
from tests.urls.conftest import get_url_data


pytestmark = pytest.mark.asyncio
msg_404 = "Данная короткая ссылка не существует. Похоже, мы её потеряли =("


async def test_redirect_nonexistent_url(client: AsyncClient):
    response = await client.get("/urls/test")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"error": True, "message": msg_404, "details": None}


async def test_redirect_url_ok(client: AsyncClient, url: models.Url):
    response = await client.get(f"/urls/{url.id}")
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT


async def test_create_url(client: AsyncClient):
    response = await client.post("/urls", json={"url": get_url_data()["url"]})
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert "url_short" in response_json
