import aioredis
from aioredis import Redis

from app.config import settings
from app.db import async_session


async def get_db():
    db = async_session()
    try:
        yield db
    finally:
        await db.close()


redis: Redis = aioredis.from_url(settings.REDIS_URI, encoding="utf-8", decode_responses=True)
