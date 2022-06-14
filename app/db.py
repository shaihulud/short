from typing import Any, Optional, Type, TypeVar

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


engine = create_async_engine(
    settings.DB_DSN,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    future=True,
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession, future=True, autoflush=False)

TBase = TypeVar("TBase", bound="EmptyBaseModel")
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class EmptyBaseModel(Base):  # type: ignore
    """
    Абстрактная базовая модель для наследования SQLAlchemy моделей.
    Содержит методы доступа и поиска по БД.
    """

    __abstract__ = True

    def __str__(self):
        return f"<{type(self).__name__}({self.id=})>"

    @classmethod
    async def get_by_id(cls: Type[TBase], session: AsyncSession, object_id: Any) -> Optional[TBase]:
        """
        Получает объект по его id == object_id.
        """
        query = sa.select(cls).where(cls.id == object_id)
        session_execute = await session.execute(query)
        return session_execute.scalars().first()

    @classmethod
    async def delete_by_id(cls: Type[TBase], session: AsyncSession, object_id: Any) -> None:
        """
        Удаляет объект по его id == object_id.
        """
        query = sa.delete(cls).where(cls.id == object_id)
        await session.execute(query)
