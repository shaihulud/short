from typing import Any, Dict

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.apps.urls import models


@pytest.fixture
async def url(db: AsyncSession):
    instance = models.Url(**get_url_data())
    db.add(instance)
    await db.flush()
    await db.commit()
    return instance


@pytest.fixture
async def url_stats(db: AsyncSession, url: models.Url):
    instance = models.UrlStats(url_id=url.id)
    db.add(instance)
    await db.flush()
    await db.commit()
    return instance


def get_url_data() -> Dict[str, Any]:
    return {
        "id": "QwErTy",
        "url": "http://example.com/",
    }
