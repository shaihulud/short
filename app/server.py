import asyncio

from fastapi import FastAPI

from app.api.base import router as base_router
from app.apps.urls import models
from app.apps.urls.api.urls import router as urls_router
from app.config import settings
from app.exceptions import setup_exceptions
from app.logging import configure_logging
from app.utils import do_stuff_periodically


def setup_routers(application: FastAPI) -> None:
    application.include_router(urls_router, prefix="/urls", tags=["urls"])
    application.include_router(base_router, tags=["probe"])


def get_app(app_name: str) -> FastAPI:
    application = FastAPI(
        title=app_name,
        root_path=settings.ROOT_PATH,
        debug=settings.DEBUG,
    )

    configure_logging()
    setup_exceptions(application)
    setup_routers(application)
    return application


app = get_app(app_name=settings.SERVICE_NAME)


@app.on_event("startup")
async def on_startup() -> None:
    """Выполняется при старте приложения."""
    if not settings.DEBUG:
        # Запустим чистку таблиц от старых данных.
        # Для URL это данные старше, чем SHORT_URL_TTL, а для статистики - старше 24 часов, которые мы отдаём.
        # Если instance приложения будет не один, то лучше перенести такие задачи в cron / celerybeat и т.п.
        asyncio.create_task(do_stuff_periodically(1 * 60 * 60, models.Url.clean_old))
        asyncio.create_task(do_stuff_periodically(1 * 60 * 60, models.UrlStats.clean_old))
