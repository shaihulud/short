import asyncio
import logging
import random
from datetime import timedelta
from string import ascii_letters, digits
from typing import Any

from aioredis import RedisError
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.apps.urls import models, schemas
from app.config import settings
from app.deps import get_db, redis
from app.exceptions import ResourceNotFoundError
from app.utils import utcnow


logger = logging.getLogger(__name__)
router = APIRouter()
letters = [i for i in ascii_letters + digits if i not in ("i", "I", "l")]  # Удалим те, что похожи друг на друга
short_code_not_found = "Данная короткая ссылка не существует. Похоже, мы её потеряли =("


def create_short_code() -> str:
    """
    Создаёт код, который будет использован для короткой ссылки.
    """
    short_code = "".join(random.choice(letters) for _ in range(models.SHORT_CODE_LEN))
    return short_code


async def create_unique_short_code(session: AsyncSession) -> str:
    """
    Создаёт уникальный код, который будет использован для короткой ссылки.
    Честно говоря мне не нравится такой метод, с проверкой в БД. Можно было бы
    подумать про последовательную генерацию "кодов", но не хотелось бы чтобы
    люди могли вручную подбирать чужие ссылки (когда код непоследователен, а
    БД далека от заполнения, шанс такого "попадания" невелик). Так же можно было
    бы придумать хеш-функцию для длинного УРЛа, но в ТЗ чётко сказано, что
    короткой ссылке можно обновить длинную на любую. Но даже при таком способе
    проверки в БД при 59 символах и длине кода = 6 будет существовать 42млрд.
    комбинаций и потому статистически вероятность коллизий мала, а, значит, и
    количество лишних запросов в БД будет небольшим.
    Если же мы будем популярны, то стоит поменять длину на 7, что составит
    2.5 трлн. комбинаций.
    Вопрос хранилища встанет гораздо раньше и начать, наверное, стоит с партицирования
    в Postgres, возможно, использования SSD и т.п. улучшений.
    """
    while True:
        short_code = create_short_code()
        url_obj = await models.Url.get_by_id(session, short_code)
        if not url_obj:
            return short_code


async def redis_set(short_code: str, long_url: str) -> None:
    """
    Шорткат для записи длинного урла long_url в Redis по ключу,
    состоящему из "кода" short_code короткого урла.
    """
    await redis.set(settings.REDIS_URL_KEY.format(short_code), long_url, ex=settings.REDIS_URL_TTL)


@router.post("", response_model=schemas.Url)
async def create_short_url(data: schemas.UrlCreate, request: Request, session: AsyncSession = Depends(get_db)) -> Any:
    """
    Генерирует новый короткий URL, и возвращает его в
    формате <hostname>/urls/<short code>, где <short code>
    это короткий уникальный "код" ссылки.
    """
    short_code = await create_unique_short_code(session)

    url_obj = models.Url(**data.dict(), id=short_code)
    session.add(url_obj)
    await session.flush()
    await session.commit()

    # Создадим отложенную таску (чтобы юзер не ждал) с записью соответствий URL в Redis.
    asyncio.create_task(redis_set(short_code, data.url))
    return schemas.Url(url_short=request.url_for("redirect_to_long_url", short_code=short_code))


@router.get("/{short_code}")
async def redirect_to_long_url(short_code: str, session: AsyncSession = Depends(get_db)) -> Any:
    """
    Перенаправляет пользователя на оригинальную ссылку
    по уникальному "коду" short_code из короткой ссылки.
    """
    try:
        redirect_url = await redis.get(settings.REDIS_URL_KEY.format(short_code))
    except RedisError:
        redirect_url = None
        logger.exception("Error while getting data from Redis")

    if redirect_url:
        asyncio.create_task(models.UrlStats.create(short_code))
        return RedirectResponse(redirect_url)

    url_obj = await models.Url.get_by_id(session, short_code)
    if not url_obj:
        raise ResourceNotFoundError(short_code_not_found)

    asyncio.create_task(redis_set(short_code, url_obj.url))
    asyncio.create_task(models.UrlStats.create(short_code))
    return RedirectResponse(url_obj.url)


@router.get("/{short_code}/stats", response_model=schemas.StatsResponse)
async def get_short_url_stats(short_code: str, session: AsyncSession = Depends(get_db)) -> Any:
    """
    Возвращает количество переходов
    по ссылке за последние 24 часа.
    """
    url_obj = await models.Url.get_by_id(session, short_code)
    if not url_obj:
        raise ResourceNotFoundError(short_code_not_found)

    dt_to = utcnow()
    dt_from = dt_to - timedelta(hours=24)
    number_of_redirects = await models.UrlStats.count_hours_stats(session, short_code, dt_from, dt_to)
    return schemas.StatsResponse(redirects_in_24_hours=number_of_redirects)


@router.put("/{short_code}", response_model=schemas.Url)
async def update_short_url(
    short_code: str, data: schemas.UrlCreate, request: Request, session: AsyncSession = Depends(get_db)
) -> Any:
    """
    Для короткой ссылки с "кодом" short_code
    обновляет на основе data "длинную" ссылку.
    """
    url_obj = await models.Url.get_by_id(session, short_code)
    if not url_obj:
        raise ResourceNotFoundError(short_code_not_found)

    url_obj.url = data.url
    session.add(url_obj)
    await session.flush()
    await session.commit()

    asyncio.create_task(redis_set(short_code, data.url))
    return schemas.Url(url_short=request.url_for("redirect_to_long_url", short_code=short_code))


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(short_code: str, session: AsyncSession = Depends(get_db)) -> Any:
    """
    Удаляет короткую ссылку с "кодом" short_code.
    """
    await models.Url.delete_by_id(session, short_code)
    await models.UrlStats.delete_by_url_id(session, short_code)
    await session.commit()
    await redis.delete(settings.REDIS_URL_KEY.format(short_code))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
