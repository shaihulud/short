from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import operators

from app.config import settings
from app.db import async_session, EmptyBaseModel
from app.utils import utcnow


SHORT_CODE_LEN = 6  # Длина "кода" короткой ссылки


class Url(EmptyBaseModel):
    __tablename__ = "urls"

    id = sa.Column(sa.String(SHORT_CODE_LEN), primary_key=True)
    url = sa.Column(sa.Text, nullable=False, unique=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=utcnow, index=True)

    @classmethod
    async def clean_old(cls) -> None:
        """
        Удаляет ссылки, старше, чем SHORT_URL_TTL секунд.
        """
        dt = utcnow() - timedelta(seconds=settings.SHORT_URL_TTL)

        # Redis можно не чистить, т.к. в течении суток данные сами удалятся. Либо, если необходимо, можно удалить.
        # Когда данных в БД станет много, то запрос может начать работать медленно, тогда поможет удаление батчами.
        async with async_session() as session:
            query = sa.delete(cls).where(operators.lt(cls.created_at, dt))
            await session.execute(query)
            await session.commit()


class UrlStats(EmptyBaseModel):
    __tablename__ = "url_stats"

    id = sa.Column(sa.Integer, primary_key=True)
    url_id = sa.Column(sa.String(SHORT_CODE_LEN), sa.ForeignKey("urls.id"), nullable=False, unique=False)
    created_at = sa.Column(sa.DateTime(timezone=True), default=utcnow)

    @classmethod
    async def create(cls, short_code: str) -> None:
        """
        Добавляет в БД статистику о переходе по short_code.
        """
        async with async_session() as session:
            stats_obj = cls(url_id=short_code)
            session.add(stats_obj)
            await session.flush()
            await session.commit()

    @classmethod
    async def delete_by_url_id(cls, session: AsyncSession, url_id: str) -> None:
        """
        Удаляет объект по его id == object_id.
        """
        query = sa.delete(cls).where(cls.url_id == url_id)
        await session.execute(query)

    @classmethod
    async def count_hours_stats(cls, session: AsyncSession, url_id: str, dt_from: datetime, dt_to: datetime) -> int:
        """
        Возвращает количество переходов по ссылке за последние 24 часа.
        """
        query = sa.select(cls).where(
            sa.and_(
                operators.eq(cls.url_id, url_id),
                operators.gt(cls.created_at, dt_from),
                operators.le(cls.created_at, dt_to),
            )
        )
        total = await session.scalar(sa.select([sa.func.count()]).select_from(query))
        return total

    @classmethod
    async def clean_old(cls) -> None:
        """
        Удаляет статистику, старше 24 часов.
        """
        dt = utcnow() - timedelta(hours=24)

        # Когда данных в БД станет много, то запрос может начать работать медленно, тогда поможет удаление батчами.
        async with async_session() as session:
            query = sa.delete(cls).where(operators.lt(cls.created_at, dt))
            await session.execute(query)
            await session.commit()
